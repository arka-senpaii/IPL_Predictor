"""
IPL Match Winner Prediction - Deep Learning Model (TensorFlow/Keras)
Author: Antigravity AI
Description: Trains a neural network on match-level features derived from
             ball-by-ball IPL data. Exports model weights + scaler as JSON.
"""

import pandas as pd
import numpy as np
import json
import os
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# ─────────────────────────────────────────────
# GPU Configuration
# ─────────────────────────────────────────────
gpus = tf.config.list_physical_devices("GPU")
if gpus:
    print(f"\n🖥️  GPU(s) detected: {[g.name for g in gpus]}")
    try:
        for gpu in gpus:
            # Allow memory growth — prevents TF from grabbing all VRAM at once
            tf.config.experimental.set_memory_growth(gpu, True)
        # Enable mixed precision (float16) for faster training on modern GPUs
        tf.keras.mixed_precision.set_global_policy("mixed_float16")
        print("   ✅ GPU memory growth enabled | Mixed precision: float16")
    except RuntimeError as e:
        print(f"   ⚠️  GPU config error: {e}")
else:
    print("\n⚠️  No GPU detected — training on CPU (may be slower).")
    print("   To use GPU, install: pip install tensorflow[and-cuda]")

# ─────────────────────────────────────────────
# 1. Load & Pre-process Data
# ─────────────────────────────────────────────
print("=" * 60)
print("IPL Match Winner Prediction - TensorFlow Deep Learning Model")
print("=" * 60)
print("\n[1/6] Loading IPL.csv ...")

df = pd.read_csv("IPL.csv")
print(f"     Loaded {len(df):,} rows × {df.shape[1]} columns")

# Keep only rows where match_won_by is known
df = df.dropna(subset=["match_won_by", "batting_team", "bowling_team", "venue"])

# ─────────────────────────────────────────────
# 2. Build Match-Level Summary
# ─────────────────────────────────────────────
print("\n[2/6] Aggregating to match-level features ...")

# Per match metadata (take first row per match_id)
match_meta = df.groupby("match_id").first().reset_index()[[
    "match_id", "date", "batting_team", "bowling_team", "venue",
    "city", "toss_winner", "toss_decision", "match_won_by",
    "win_outcome", "season", "year", "stage",
    "player_of_match"
]]

# Per innings total runs and wickets
innings_agg = df.groupby(["match_id", "innings"]).agg(
    total_runs=("runs_total", "sum"),
    total_wickets=("wicket_kind", lambda x: (x.notna() & (x != "")).sum()),
).reset_index()

# Innings 1
inn1 = innings_agg[innings_agg["innings"] == 1].rename(
    columns={"total_runs": "inn1_runs", "total_wickets": "inn1_wkts"}
).drop(columns="innings")

# Innings 2
inn2 = innings_agg[innings_agg["innings"] == 2].rename(
    columns={"total_runs": "inn2_runs", "total_wickets": "inn2_wkts"}
).drop(columns="innings")

matches = match_meta.merge(inn1, on="match_id", how="left")
matches = matches.merge(inn2, on="match_id", how="left")
matches["inn1_runs"] = matches["inn1_runs"].fillna(0).astype(int)
matches["inn2_runs"] = matches["inn2_runs"].fillna(0).astype(int)
matches["inn1_wkts"] = matches["inn1_wkts"].fillna(0).astype(int)
matches["inn2_wkts"] = matches["inn2_wkts"].fillna(0).astype(int)

# Determine team1/team2 and winner label
matches["team1"] = matches["batting_team"]
matches["team2"] = matches["bowling_team"]

# winner is 1 if team1 (bat first) won, else 0
matches["winner_label"] = (matches["match_won_by"] == matches["team1"]).astype(int)

print(f"     {len(matches):,} unique matches found")

# ─────────────────────────────────────────────
# 3. Feature Engineering
# ─────────────────────────────────────────────
print("\n[3/6] Engineering features ...")

# Sort by date
matches["date"] = pd.to_datetime(matches["date"])
matches = matches.sort_values("date").reset_index(drop=True)

# Encode categorical variables
le_team = LabelEncoder()
all_teams = list(set(list(matches["team1"].unique()) + list(matches["team2"].unique())))
le_team.fit(all_teams)

le_venue = LabelEncoder()
le_venue.fit(matches["venue"])

le_toss = LabelEncoder()
le_toss.fit(["bat", "field"])

# Team win statistics – rolling (computed before each match)
team_wins = {t: 0 for t in all_teams}
team_matches = {t: 0 for t in all_teams}

# H2H stats
from collections import defaultdict
h2h_wins = defaultdict(lambda: defaultdict(int))
h2h_matches = defaultdict(lambda: defaultdict(int))

X_rows = []
y_rows = []

for _, row in matches.iterrows():
    t1 = row["team1"]
    t2 = row["team2"]
    venue = row["venue"]
    toss_win_t1 = int(row["toss_winner"] == t1)
    toss_dec = 1 if row["toss_decision"] == "bat" else 0

    # Win rates (with smoothing)
    t1_wr = (team_wins[t1] + 1) / (team_matches[t1] + 2)
    t2_wr = (team_wins[t2] + 1) / (team_matches[t2] + 2)

    h2h_total = h2h_matches[t1][t2] + 1
    h2h_t1_wr = (h2h_wins[t1][t2] + 0.5) / h2h_total

    try:
        t1_enc = le_team.transform([t1])[0]
        t2_enc = le_team.transform([t2])[0]
        v_enc = le_venue.transform([venue])[0]
    except Exception:
        continue

    season_num = int(str(row["season"]).split("/")[0])

    feat = [
        t1_enc, t2_enc, v_enc,
        toss_win_t1, toss_dec,
        t1_wr, t2_wr,
        h2h_t1_wr,
        season_num,
    ]

    X_rows.append(feat)
    y_rows.append(row["winner_label"])

    # Update running stats AFTER adding to dataset (prevent leakage)
    winner = row["match_won_by"]
    team_matches[t1] += 1
    team_matches[t2] += 1
    if winner == t1:
        team_wins[t1] += 1
        h2h_wins[t1][t2] += 1
    else:
        team_wins[t2] += 1
        h2h_wins[t2][t1] += 1
    h2h_matches[t1][t2] += 1
    h2h_matches[t2][t1] += 1

X = np.array(X_rows, dtype=np.float32)
y = np.array(y_rows, dtype=np.float32)

print(f"     Feature matrix: {X.shape}  |  Labels: {y.shape}")
print(f"     Label balance — team1 wins: {y.mean():.1%}")

# Scale features
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# ─────────────────────────────────────────────
# 4. Build & Train TF Model
# ─────────────────────────────────────────────
print("\n[4/6] Building TensorFlow neural network ...")

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

model = keras.Sequential([
    layers.Input(shape=(X.shape[1],)),
    layers.Dense(128, activation="relu"),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(64, activation="relu"),
    layers.BatchNormalization(),
    layers.Dropout(0.2),
    layers.Dense(32, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.summary()

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=15, restore_best_weights=True
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=7, min_lr=1e-5
    ),
]

print("\n[5/6] Training model ...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=150,
    batch_size=32,
    callbacks=callbacks,
    verbose=1,
)

# Evaluate
y_pred_prob = model.predict(X_test).flatten()
y_pred = (y_pred_prob > 0.5).astype(int)
acc = accuracy_score(y_test, y_pred)
print(f"\n  ✅ Test Accuracy: {acc:.4f} ({acc*100:.1f}%)")
print(classification_report(y_test, y_pred, target_names=["team2 wins", "team1 wins"]))

# ─────────────────────────────────────────────
# 5. Export Model + Preprocessor as JSON
# ─────────────────────────────────────────────
print("\n[6/6] Exporting model weights and scaler to docs/data/ ...")

os.makedirs("docs/data", exist_ok=True)

# Export scaler parameters
scaler_json = {
    "min_": scaler.data_min_.tolist(),
    "scale_": scaler.scale_.tolist(),
    "data_min_": scaler.data_min_.tolist(),
    "data_max_": scaler.data_max_.tolist(),
}
with open("docs/data/scaler.json", "w") as f:
    json.dump(scaler_json, f)

# Export label encoders
encoders_json = {
    "teams": list(le_team.classes_),
    "venues": list(le_venue.classes_),
}
with open("docs/data/encoders.json", "w") as f:
    json.dump(encoders_json, f, indent=2)

# Export team stats for use in predictions
team_stats = {}
for t in all_teams:
    team_stats[t] = {
        "matches": team_matches[t],
        "wins": team_wins[t],
        "win_rate": round(team_wins[t] / max(team_matches[t], 1), 4),
    }
with open("docs/data/team_stats_model.json", "w") as f:
    json.dump(team_stats, f, indent=2)

# Export training history
history_json = {
    "loss": [float(v) for v in history.history["loss"]],
    "val_loss": [float(v) for v in history.history["val_loss"]],
    "accuracy": [float(v) for v in history.history["accuracy"]],
    "val_accuracy": [float(v) for v in history.history["val_accuracy"]],
    "test_accuracy": round(float(acc), 4),
    "epochs": len(history.history["loss"]),
}
with open("docs/data/training_history.json", "w") as f:
    json.dump(history_json, f, indent=2)

# Save the full Keras model (for local use / further training)
model.save("ipl_model.keras")
print("  ✅ Keras model saved: ipl_model.keras")

# ---- Export weights layer-by-layer as JSON (for TF.js-style inference) ----
weights_list = []
for layer in model.layers:
    w = layer.get_weights()
    if len(w) > 0:
        weights_list.append({
            "name": layer.name,
            "type": layer.__class__.__name__,
            "weights": [arr.tolist() for arr in w],
        })

# Compute team win-rate lookup table
# Generate predictions for all team-pair combinations
print("\n  Generating win-probability for all team pairs + venues ...")

team_list = list(le_team.classes_)
venue_list = list(le_venue.classes_)

predictions = {}
for i, t1 in enumerate(team_list):
    if t1 not in team_stats:
        continue
    for t2 in team_list:
        if t1 == t2 or t2 not in team_stats:
            continue
        key = f"{t1} vs {t2}"
        t1_wr = team_stats[t1]["win_rate"]
        t2_wr = team_stats[t2]["win_rate"]
        h2h_t1 = 0.5  # neutral for prediction UI

        venue_preds = {}
        for v in venue_list[:30]:  # top 30 venues
            try:
                t1_enc = le_team.transform([t1])[0] / len(team_list)
                t2_enc = le_team.transform([t2])[0] / len(team_list)
                v_enc = le_venue.transform([v])[0] / len(venue_list)
            except Exception:
                continue

            feat = np.array([[
                t1_enc * len(team_list), t2_enc * len(team_list), v_enc * len(venue_list),
                1, 1, t1_wr, t2_wr, h2h_t1, 2024
            ]], dtype=np.float32)
            feat_scaled = scaler.transform(feat)
            prob = float(model.predict(feat_scaled, verbose=0)[0][0])
            venue_preds[v] = round(prob, 4)

        # Default (average across venues)
        if venue_preds:
            default_prob = round(sum(venue_preds.values()) / len(venue_preds), 4)
        else:
            default_prob = 0.5

        predictions[key] = {
            "team1": t1,
            "team2": t2,
            "team1_win_prob": default_prob,
            "team2_win_prob": round(1 - default_prob, 4),
            "by_venue": venue_preds,
        }

with open("docs/data/predictions.json", "w") as f:
    json.dump(predictions, f)

print(f"  ✅ Generated {len(predictions)} matchup predictions")

print("\n" + "=" * 60)
print("Training complete! All output written to docs/data/")
print("Next step: run  python generate_data.py")
print("=" * 60)
