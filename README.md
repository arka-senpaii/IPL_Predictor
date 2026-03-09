# 🏏 IPL Match Predictor

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> AI-powered IPL match winner prediction using TensorFlow Deep Learning — fully hosted statically on GitHub Pages.

An advanced machine learning project that predicts the outcomes of Indian Premier League (IPL) matches. It trains a Deep Neural Network on 278,000+ balls of historical data from 2008 to 2024 to provide highly accurate win probabilities, wrapped in a beautiful, premium dark-themed static website.

**[🌐 View Live Demo](https://arka-senpaii.github.io/IPL_Predictor/)**

---

## ✨ Features

- **🤖 Deep Learning Engine**: A sophisticated Neural Network built with TensorFlow/Keras, leveraging historical data for precise match outcome predictions.
- **🔮 Match Prediction Tool**: Select any two IPL teams and a venue to instantly get AI-generated win probabilities in a dynamic interface.
- **📊 Rich Interactive Visualizations**: Explore match details with dynamic Chart.js graphs, including score progressions, runs-per-over analysis, and wickets timelines.
- **🏟️ Venues & Grounds Gallery**: Browse through all IPL stadiums, view high-quality images downloaded directly from source, and explore venue-specific statistics.
- **👕 Detailed Team Analytics**: Comprehensive stats for every IPL franchise, including historical win rates, top performers, and head-to-head records.
- **🏆 Season History**: A complete archive of all IPL seasons, showcasing champions, runners-up, and Orange/Purple Cap winners.
- **⚡ 100% Serverless**: All complex predictions and statistical aggregates are pre-computed during the build phase via Python scripts, allowing the entire site to be hosted statically with zero backend latency.

---

## 🛠️ Tech Stack

- **Machine Learning**: Python, TensorFlow 2.13+, Keras, Pandas, Scikit-learn, Numpy
- **Frontend**: Vanilla HTML5, CSS3 (Premium Dark Theme), JavaScript (ES6+ Modules)
- **Data Visualization**: Chart.js
- **Deployment**: GitHub Pages (fully automated pipeline via Actions)

---

## 🚀 Local Deployment & Setup

Follow these steps to run the training pipeline and serve the application locally.

### 1. Clone the Repository
```bash
git clone https://github.com/arka-senpaii/IPL_Predictor.git
cd IPL_Predictor
```

### 2. Install Dependencies
It is highly recommended to use a virtual environment or Conda environment to manage the Python dependencies.

```bash
# Using pip
pip install -r requirements.txt
```

### 3. Model Training
Train the deep learning model. A CUDA-enabled GPU is highly recommended for faster training times, but CPU will work perfectly fine.

```bash
python train_model.py
```
*Note: This will read the `IPL.csv` dataset and output the trained model as `ipl_model.keras`.*

### 4. Fetching Assets & Ground Images
Run the script to scrape Wikipedia and ensure all team logos and venue images are correctly saved locally.
```bash
python download_assets.py
```

### 5. Generate Website Data
Process the dataset and run the pre-computations for the frontend static site based on the trained model and historical records.

```bash
python generate_data.py
```
*This generates necessary `.json` files into the `docs/data/` directory.*

### 6. Serve the Local Environment
Launch a local HTTP server to preview the site.

```bash
# Windows
cd docs
python -m http.server 8000
```
Navigate to `http://localhost:8000` in your web browser.

---

## 🧠 Model Architecture & Methodology

### Dataset
The model and website are powered by `IPL.csv`, a massive, ball-by-ball, comprehensive dataset encompassing every IPL match from the inaugural 2008 season all the way through 2024.

### Features
To prevent data leakage while maximizing predictive power, the model uses:
- **Historical Win Rates**: Rolling averages calculated prior to the match in question.
- **Head-to-Head Records**: Team vs. Team historical dominance.
- **Contextual Data**: Venue variables, Toss Winners, and Toss Decisions.
- **Categorical Encodings**: One-hot encoding alongside Scikit-learn's `LabelEncoder` for team and stadium names.

### Neural Network Design
- **Architecture**: A robust 3-layer Dense Neural Network configuration.
- **Regularization**: Extensive use of Batch Normalization (`BatchNormalization`) and Dropout layers to prevent overfitting to historically dominant teams.
- **Optimization**: Trained using early stopping callbacks to capture the optimally converged weights.

---

## 📂 Repository Structure

```text
IPL_Predictor/
├── IPL.csv                  # Raw ball-by-ball dataset (2008-2024)
├── train_model.py           # TensorFlow/Keras deep learning pipeline
├── generate_data.py         # Data processing & JSON generation for the frontend
├── download_assets.py       # Script to fetch team logos and ground images
├── ipl_model.keras          # Saved model weights
├── requirements.txt         # Python package dependencies
├── docs/                    # Static Web Application (Frontend)
│   ├── index.html           # Dashboard & Prediction interface
│   ├── matches.html         # Historical matches explorer
│   ├── match.html           # Deep-dive match statistics
│   ├── teams.html           # Franchise analytics & H2H
│   ├── seasons.html         # Championship history
│   ├── venues.html          # Stadium gallery
│   ├── css/                 # Styling (Premium Dark Theme)
│   ├── js/                  # App logic, charting components, routing
│   ├── data/                # Pre-computed datasets (JSON)
│   └── assets/              # Images, icons, and static assets
└── .github/workflows/       # CI/CD pipelines for automatic deployment (pages.yml)
```

---

## ☁️ Production Deployment

This project is configured for seamless deployment to GitHub Pages using the `docs` folder as the root.

**GitHub Pages Automation:**
1. Push your code to the `main` branch.
2. The included GitHub Actions workflow will automatically trigger (if workflow exists) OR you can set pages to deploy from the `docs` directory.
3. Turn on Pages in Settings: Go to **Settings → Pages** and ensure the source is set to build and deploy from the `docs` path on the `main` branch.

---

<div align="center">
  <i>Built with ❤️ using TensorFlow, vanilla web technologies, and data-driven insights.</i>
</div>