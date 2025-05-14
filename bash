#!/bin/bash

# Create core directories
mkdir -p apex_arc/data
mkdir -p apex_arc/logs
mkdir -p apex_arc/scripts
mkdir -p apex_arc/.github/workflows

# Create empty input data placeholders
touch apex_arc/data/stats-2.csv
touch apex_arc/data/mlb_rosters_2025.csv
touch apex_arc/data/cumulative_tracking.csv

# Create empty log file
touch apex_arc/logs/sim_log.txt

# Full working Apex Arc simulation script
cat > apex_arc/scripts/run_hr_simulation.py << 'EOF'
import pandas as pd
import numpy as np
from datetime import datetime

# --- Config ---
INPUT_STATS = "../data/stats-2.csv"
INPUT_ROSTERS = "../data/mlb_rosters_2025.csv"
INPUT_TRACKING = "../data/cumulative_tracking.csv"
OUTPUT_TOP50 = "../data/apex_top50_hr_projection.csv"
LOG_FILE = "../logs/sim_log.txt"

# --- Normalize Names ---
def normalize_name(name):
    return name.replace(",", "").replace(".", "").replace(" Jr", "").strip().lower()

# --- Load Data ---
stats = pd.read_csv(INPUT_STATS)
rosters = pd.read_csv(INPUT_ROSTERS)
tracking = pd.read_csv(INPUT_TRACKING)

stats['norm_name'] = stats['last_name, first_name'].apply(normalize_name)
rosters['norm_name'] = rosters['player_name'].apply(normalize_name)

# --- Merge Stats + Rosters ---
players = pd.merge(stats, rosters, on='player_id', how='left')

# --- Recent HR Performance ---
recent_hr = (
    tracking.groupby('Player')
    .agg({'Actual_HR': 'sum', 'Result': lambda x: (x == "Surprise").sum()})
    .rename(columns={'Actual_HR': 'recent_HR', 'Result': 'recent_Surprise_HR'})
    .reset_index()
)
recent_hr['Player_norm'] = recent_hr['Player'].apply(lambda x: normalize_name(x) if isinstance(x, str) else "")
players['Player_norm'] = players['player_name'].apply(normalize_name)

players = pd.merge(players, recent_hr, on='Player_norm', how='left')
players['recent_HR'] = players['recent_HR'].fillna(0)
players['recent_Surprise_HR'] = players['recent_Surprise_HR'].fillna(0)

# --- HR Probability Model ---
def calc_hr_prob(row):
    ev = float(row.get('avg_best_speed', 0))
    la = float(row.get('sweet_spot_percent', 0))
    barrel = float(row.get('barrel_batted_rate', 0))
    hardhit = float(row.get('hard_hit_percent', 0))
    recent_hr_bonus = 0.5 * row.get('recent_HR', 0)
    surprise_hr_bonus = 0.5 * row.get('recent_Surprise_HR', 0)

    prob = (
        0.25 * (ev / 110) +
        0.25 * (barrel / 20) +
        0.2 * (hardhit / 60) +
        0.15 * (la / 50) +
        0.05 * recent_hr_bonus +
        0.05 * surprise_hr_bonus
    )
    return min(prob, 1.0)

players['HR_Prob'] = players.apply(calc_hr_prob, axis=1)
players['HR_Score'] = (players['HR_Prob'] * 20).round().astype(int)

# --- Top 50 Output ---
top50 = players.sort_values(by='HR_Prob', ascending=False).head(50)[
    ['player_name', 'team', 'HR_Prob', 'HR_Score', 'recent_HR', 'recent_Surprise_HR']
]
top50.to_csv(OUTPUT_TOP50, index=False)

# --- Log Completion ---
with open(LOG_FILE, "a") as log:
    log.write(f"[{datetime.now()}] Simulation complete. Top 50 saved to {OUTPUT_TOP50}\n")
EOF

# GitHub Actions workflow
cat > apex_arc/.github/workflows/simulate.yml << 'EOF'
name: Run Daily HR Simulation

on:
  schedule:
    - cron: '0 12 * * *'  # 5 AM PT daily
  workflow_dispatch:

jobs:
  simulate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.10

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run HR Simulation
        run: python scripts/run_hr_simulation.py

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: apex-top50
          path: data/apex_top50_hr_projection.csv
EOF

# Replit launch file
cat > apex_arc/.replit << 'EOF'
run = "python3 scripts/run_hr_simulation.py"
EOF

# Replit nix environment
cat > apex_arc/replit.nix << 'EOF'
{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
  ];
}
EOF

# Requirements
cat > apex_arc/requirements.txt << 'EOF'
pandas
numpy
EOF

# README
cat > apex_arc/README.md << 'EOF'
# Apex Arc HR Prediction System

Automated daily home run predictions using advanced stat overlays, recent form, and probability modeling.

## To Run Locally
```bash
python scripts/run_hr_simulation.py