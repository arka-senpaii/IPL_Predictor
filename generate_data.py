"""
IPL Data Generator
Reads IPL.csv and generates all JSON data files needed by the static website:
  docs/data/matches.json
  docs/data/teams.json
  docs/data/h2h.json
  docs/data/seasons.json
  docs/data/venues.json
"""

import pandas as pd
import numpy as np
import json
import os
from collections import defaultdict

print("=" * 60)
print("IPL Data Generator — Building Website JSON Files")
print("=" * 60)

os.makedirs("docs/data", exist_ok=True)

# ══════════════════════════════════════════════════════════════
# Normalization mappings: merge duplicate venues & team names
# ══════════════════════════════════════════════════════════════

VENUE_MAP = {
    # Arun Jaitley Stadium / Feroz Shah Kotla → same ground in Delhi
    "Arun Jaitley Stadium":          "Arun Jaitley Stadium, Delhi",
    "Feroz Shah Kotla":              "Arun Jaitley Stadium, Delhi",
    # Brabourne Stadium
    "Brabourne Stadium":             "Brabourne Stadium, Mumbai",
    # Dr DY Patil
    "Dr DY Patil Sports Academy":    "Dr DY Patil Sports Academy, Mumbai",
    # ACA-VDCA Visakhapatnam
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium":
        "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam",
    # Eden Gardens
    "Eden Gardens":                  "Eden Gardens, Kolkata",
    # Chinnaswamy Stadium variants
    "M Chinnaswamy Stadium":         "M Chinnaswamy Stadium, Bengaluru",
    "M.Chinnaswamy Stadium":         "M Chinnaswamy Stadium, Bengaluru",
    # MA Chidambaram Stadium variants
    "MA Chidambaram Stadium":        "MA Chidambaram Stadium, Chepauk, Chennai",
    "MA Chidambaram Stadium, Chepauk": "MA Chidambaram Stadium, Chepauk, Chennai",
    # HPCA Dharamsala
    "Himachal Pradesh Cricket Association Stadium":
        "Himachal Pradesh Cricket Association Stadium, Dharamsala",
    # MCA Pune
    "Maharashtra Cricket Association Stadium":
        "Maharashtra Cricket Association Stadium, Pune",
    # PCA Mohali / Chandigarh variants
    "Punjab Cricket Association IS Bindra Stadium":
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
    "Punjab Cricket Association IS Bindra Stadium, Mohali":
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
    "Punjab Cricket Association Stadium, Mohali":
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
    # Rajiv Gandhi Hyderabad variants
    "Rajiv Gandhi International Stadium":
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad",
    "Rajiv Gandhi International Stadium, Uppal":
        "Rajiv Gandhi International Stadium, Uppal, Hyderabad",
    # Sawai Mansingh
    "Sawai Mansingh Stadium":        "Sawai Mansingh Stadium, Jaipur",
    # Wankhede
    "Wankhede Stadium":              "Wankhede Stadium, Mumbai",
    # Sardar Patel / Narendra Modi (renamed)
    "Sardar Patel Stadium, Motera":  "Narendra Modi Stadium, Ahmedabad",
    # Abu Dhabi variants
    "Sheikh Zayed Stadium":          "Sheikh Zayed Stadium, Abu Dhabi",
    "Zayed Cricket Stadium, Abu Dhabi": "Sheikh Zayed Stadium, Abu Dhabi",
    # Mullanpur / New Chandigarh — same ground
    "Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh":
        "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur",
}

TEAM_MAP = {
    "Delhi Daredevils":         "Delhi Capitals",
    "Kings XI Punjab":          "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Rising Pune Supergiants":  "Rising Pune Supergiant",
}

# ─────────────────────────────────────────────
print("\n[1/6] Loading IPL.csv ...")
df = pd.read_csv("IPL.csv", low_memory=False)
df = df.dropna(subset=["match_id", "batting_team", "bowling_team", "match_won_by"])
df["date"] = pd.to_datetime(df["date"])
print(f"     {len(df):,} rows loaded")

# Apply normalization
print("     Normalizing venue and team names ...")
df["venue"] = df["venue"].replace(VENUE_MAP)
for col in ["batting_team", "bowling_team", "toss_winner", "match_won_by"]:
    df[col] = df[col].replace(TEAM_MAP)
print(f"     ✅ Normalized {len(VENUE_MAP)} venue aliases, {len(TEAM_MAP)} team aliases")

# ─────────────────────────────────────────────
print("[2/6] Building match summaries ...")

# Match-level metadata
meta_cols = [
    "match_id", "date", "batting_team", "bowling_team", "venue", "city",
    "toss_winner", "toss_decision", "match_won_by", "win_outcome",
    "season", "year", "player_of_match", "stage", "event_match_no",
    "result_type", "method"
]
meta = df.groupby("match_id").first().reset_index()[meta_cols]

# Innings totals
inn = df.groupby(["match_id", "innings"]).agg(
    runs=("runs_total", "sum"),
    wickets=("wicket_kind", lambda x: (x.notna() & (x.astype(str) != "") & (x.astype(str) != "nan")).sum()),
    balls=("valid_ball", "sum"),
).reset_index()

inn1 = inn[inn["innings"] == 1].rename(columns={"runs": "inn1_runs", "wickets": "inn1_wkts", "balls": "inn1_balls"}).drop(columns="innings")
inn2 = inn[inn["innings"] == 2].rename(columns={"runs": "inn2_runs", "wickets": "inn2_wkts", "balls": "inn2_balls"}).drop(columns="innings")

matches = meta.merge(inn1, on="match_id", how="left").merge(inn2, on="match_id", how="left")
for col in ["inn1_runs", "inn2_runs", "inn1_wkts", "inn2_wkts", "inn1_balls", "inn2_balls"]:
    matches[col] = matches[col].fillna(0).astype(int)

matches["date_str"] = matches["date"].dt.strftime("%Y-%m-%d")

# Per-match over-by-over progression (for match detail charts)
print("     Building over-by-over progression data ...")
over_prog = df.groupby(["match_id", "innings", "over"]).agg(
    runs_in_over=("runs_total", "sum"),
    wickets_in_over=("wicket_kind", lambda x: (x.notna() & (x.astype(str) != "") & (x.astype(str) != "nan")).sum()),
).reset_index()
over_prog_dict = defaultdict(lambda: defaultdict(list))
for _, row in over_prog.iterrows():
    over_prog_dict[int(row["match_id"])][int(row["innings"])].append({
        "over": int(row["over"]),
        "runs": int(row["runs_in_over"]),
        "wickets": int(row["wickets_in_over"]),
    })

# Cumulative runs per over
for mid in over_prog_dict:
    for inn_num in over_prog_dict[mid]:
        overs = sorted(over_prog_dict[mid][inn_num], key=lambda x: x["over"])
        cum = 0
        for o in overs:
            cum += o["runs"]
            o["cumulative_runs"] = cum
        over_prog_dict[mid][inn_num] = overs

# Build final matches list
matches_list = []
for _, row in matches.iterrows():
    mid = int(row["match_id"])
    record = {
        "match_id": mid,
        "date": row["date_str"],
        "season": str(row["season"]),
        "stage": str(row.get("stage", "Unknown")),
        "match_no": str(row.get("event_match_no", "")),
        "team1": str(row["batting_team"]),
        "team2": str(row["bowling_team"]),
        "venue": str(row["venue"]),
        "city": str(row.get("city", "")),
        "toss_winner": str(row["toss_winner"]),
        "toss_decision": str(row["toss_decision"]),
        "winner": str(row["match_won_by"]),
        "win_outcome": str(row.get("win_outcome", "")),
        "player_of_match": str(row.get("player_of_match", "")),
        "team1_score": int(row["inn1_runs"]),
        "team1_wickets": int(row["inn1_wkts"]),
        "team2_score": int(row["inn2_runs"]),
        "team2_wickets": int(row["inn2_wkts"]),
        "over_progression": {
            "innings1": over_prog_dict[mid].get(1, []),
            "innings2": over_prog_dict[mid].get(2, []),
        },
    }
    matches_list.append(record)

# Sort newest first
matches_list.sort(key=lambda x: x["date"], reverse=True)

with open("docs/data/matches.json", "w") as f:
    json.dump(matches_list, f, separators=(",", ":"))
print(f"     ✅ matches.json — {len(matches_list)} matches")

# ─────────────────────────────────────────────
print("[3/6] Building team statistics ...")

all_teams = sorted(set(matches["batting_team"].tolist() + matches["bowling_team"].tolist()))

team_stats = {}
for team in all_teams:
    team_matches = matches[(matches["batting_team"] == team) | (matches["bowling_team"] == team)]
    wins = (team_matches["match_won_by"] == team).sum()
    total = len(team_matches)
    losses = total - wins

    # Season-by-season
    seasons_data = {}
    for season, grp in team_matches.groupby("season"):
        s_wins = (grp["match_won_by"] == team).sum()
        seasons_data[str(season)] = {"matches": len(grp), "wins": int(s_wins)}

    # Top batsmen for this team
    team_df = df[df["batting_team"] == team]
    batters = team_df.groupby("batter")["runs_batter"].sum().sort_values(ascending=False).head(5)

    # Top bowlers for this team
    bowl_df = df[df["bowling_team"] == team]
    bowlers = bowl_df.groupby("bowler")["bowler_wicket"].sum().sort_values(ascending=False).head(5)

    team_stats[team] = {
        "team": team,
        "matches": int(total),
        "wins": int(wins),
        "losses": int(losses),
        "win_pct": round(wins / max(total, 1) * 100, 1),
        "seasons": seasons_data,
        "top_batsmen": [{"name": n, "runs": int(r)} for n, r in batters.items()],
        "top_bowlers": [{"name": n, "wickets": int(w)} for n, w in bowlers.items()],
    }

with open("docs/data/teams.json", "w") as f:
    json.dump(team_stats, f, indent=2)
print(f"     ✅ teams.json — {len(team_stats)} teams")

# ─────────────────────────────────────────────
print("[4/6] Building head-to-head stats ...")

h2h = {}
for t1 in all_teams:
    for t2 in all_teams:
        if t1 >= t2:
            continue
        h2h_matches_df = matches[
            ((matches["batting_team"] == t1) & (matches["bowling_team"] == t2)) |
            ((matches["batting_team"] == t2) & (matches["bowling_team"] == t1))
        ]
        if len(h2h_matches_df) == 0:
            continue
        t1_wins = (h2h_matches_df["match_won_by"] == t1).sum()
        t2_wins = (h2h_matches_df["match_won_by"] == t2).sum()
        key = f"{t1}||{t2}"
        h2h[key] = {
            "team1": t1, "team2": t2,
            "matches": int(len(h2h_matches_df)),
            "team1_wins": int(t1_wins),
            "team2_wins": int(t2_wins),
        }

with open("docs/data/h2h.json", "w") as f:
    json.dump(h2h, f, indent=2)
print(f"     ✅ h2h.json — {len(h2h)} pairs")

# ─────────────────────────────────────────────
print("[5/6] Building season summaries ...")

seasons = {}
for season, grp in matches.groupby("season"):
    final = grp[grp["stage"].str.contains("Final|final|final", na=False)]
    champion = final["match_won_by"].values[0] if len(final) > 0 else "Unknown"
    runner_up = ""
    if len(final) > 0:
        f_row = final.iloc[0]
        teams = {f_row["batting_team"], f_row["bowling_team"]}
        runner_up = (teams - {champion}).pop() if len(teams) == 2 else ""

    # Top scorer of season
    season_df = df[df["season"] == season]
    top_batter = season_df.groupby("batter")["runs_batter"].sum().idxmax()
    top_batter_runs = int(season_df.groupby("batter")["runs_batter"].sum().max())
    top_bowler = season_df.groupby("bowler")["bowler_wicket"].sum().idxmax()
    top_bowler_wkts = int(season_df.groupby("bowler")["bowler_wicket"].sum().max())

    seasons[str(season)] = {
        "season": str(season),
        "matches": int(len(grp)),
        "champion": champion,
        "runner_up": runner_up,
        "orange_cap": top_batter,
        "orange_cap_runs": top_batter_runs,
        "purple_cap": top_bowler,
        "purple_cap_wickets": top_bowler_wkts,
    }

with open("docs/data/seasons.json", "w") as f:
    json.dump(seasons, f, indent=2)
print(f"     ✅ seasons.json — {len(seasons)} seasons")

# ─────────────────────────────────────────────
print("[6/6] Building venue stats ...")

venues = {}
for venue, grp in matches.groupby("venue"):
    city = grp["city"].mode().values[0] if len(grp) > 0 else ""
    most_wins = grp["match_won_by"].value_counts()
    venues[venue] = {
        "venue": venue,
        "city": str(city),
        "matches": int(len(grp)),
        "most_wins": most_wins.index[0] if len(most_wins) > 0 else "",
        "most_wins_count": int(most_wins.values[0]) if len(most_wins) > 0 else 0,
        "avg_score_inn1": round(grp["inn1_runs"].mean(), 1),
        "avg_score_inn2": round(grp["inn2_runs"].mean(), 1),
    }

with open("docs/data/venues.json", "w") as f:
    json.dump(venues, f, indent=2)
print(f"     ✅ venues.json — {len(venues)} venues")

print("\n" + "=" * 60)
print("✅ All data files generated in docs/data/")
print("Next step: Open the website in browser to verify!")
print("=" * 60)
