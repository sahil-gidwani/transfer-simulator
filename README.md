# Transfer Simulator

A professional, educational platform for simulating and predicting football player performance after transfers, using both machine learning and rule-based approaches. Built with Streamlit, pandas, numpy, and scikit-learn.

## Features
- **ML-Based Prediction:** Predict post-transfer performance using a simple, interpretable ML model (Ridge, Linear, or Gradient Boosting) with Goals per 90, Age, and Position Group as features.
- **Rule-Based Simulation:** Simulate player performance using league/team ratings and position group scaling, with clear comparative visualizations.
- **Interactive Streamlit UI:** Clean, professional interface with EDA, scenario configuration, and result visualization.
- **Modular Codebase:** Utilities for data loading, mapping, and simulation logic.
- **Comprehensive Documentation:** File-by-file project overview and setup instructions.

## Project Structure

```
transfer-simulator/
├── Home.py                        # Main Streamlit landing page
├── LICENSE
├── README.md                      # (This file)
├── requirements.txt               # Python dependencies
├── data/
│   ├── filtered_leagues.csv       # Real transfer data
│   └── power-rankings-teams.csv   # Team/league ratings
├── pages/
│   ├── 1_ML_Performance_Prediction.py   # ML-based prediction app
│   └── 2_Rule_Based_Transfer_Simulation.py # Rule-based simulation app
└── utils/
    ├── __init__.py
    ├── data_utils.py              # Data loading utilities
    ├── mapper.py                  # Position group mapping
    ├── power_rankings.py          # Team/league ratings utilities
    ├── transfer_simulator.py      # Rule-based simulation logic
    └── transfers_utils.py         # Dummy data generation, transfer extraction
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sahil-gidwani/transfer-simulator.git
   cd transfer-simulator
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Streamlit app:**
   ```bash
   streamlit run Home.py
   ```
   - The app will open in your browser. Use the sidebar to navigate between ML-based and Rule-based simulation pages.

## File-by-File Overview

- **Home.py**: Main Streamlit entry point. Provides project overview and navigation.
- **pages/1_ML_Performance_Prediction.py**: ML-based prediction page. Includes EDA, model training, and interactive prediction.
- **pages/2_Rule_Based_Transfer_Simulation.py**: Rule-based simulation page. Allows scenario configuration and displays comparative results.
- **utils/data_utils.py**: Functions for loading and preprocessing data.
- **utils/mapper.py**: Maps player positions to position groups.
- **utils/power_rankings.py**: Loads and manages team/league ratings.
- **utils/transfer_simulator.py**: Contains `simulate_player_transfer` and related rule-based logic.
- **utils/transfers_utils.py**: Generates dummy data and extracts transfer scenarios.
- **data/filtered_leagues.csv**: Real transfer data for simulation and EDA.
- **data/power-rankings-teams.csv**: Team/league ratings for scaling.
- **requirements.txt**: All required Python packages.
- **README.md**: This documentation file.

## Usage
- **ML-Based Prediction:**
  - Explore EDA, train the model, and predict post-transfer performance interactively.
- **Rule-Based Simulation:**
  - Configure transfer scenarios, view current and predicted metrics, and compare with position group averages.

## Notes
- The app is designed for educational and demonstration purposes.
- Dummy data generation is included for experimentation.
- For best results, use real transfer data and adjust simulation parameters as needed.

## License
See LICENSE for details.
