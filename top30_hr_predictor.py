# models/top30_hr_predictor.py
# Apex Arc Top 30 HR Predictor

import pandas as pd
import numpy as np
from overlays.weather_overlay import apply_weather_overlay
from overlays.park_factor_overlay import apply_park_factor_overlay
from overlays.pitcher_overlay import apply_pitcher_overlay
from overlays.batter_overlay import apply_batter_overlay
import os
from datetime import date
from utils.data_fetcher import get_raw_player_data

def generate_top30_predictions():
    """
    Generates the top 30 players most likely to hit a home run today,
    applying multiple overlays to determine final HR probability scores.
    """
    print(">> Generating Top 30 HR Predictions...")

    # 1. Load Raw Player Data
    player_df = get_raw_player_data()

    # 2. Apply Overlays
    player_df = apply_weather_overlay(player_df)
    player_df = apply_park_factor_overlay(player_df)
    player_df = apply_pitcher_overlay(player_df)
    player_df = apply_batter_overlay(player_df)

    # 3. Generate HR Probability Score
    # (Simple weighted sum — can evolve into XGBoost/lightGBM later)
    player_df['HR_Score'] = (
        0.4 * player_df['Barrel%'] +
        0.3 * player_df['LaunchAngleSweetSpot%'] +
        0.2 * player_df['xISO'] +
        0.1 * player_df['WeatherBoost'] +
        player_df['ParkFactorBoost'] +
        player_df['PitcherHRBoost'] +
        player_df['HotStreakBoost']
    )

    # 4. Rank Players
    top30 = player_df.sort_values(by='HR_Score', ascending=False).head(30).copy()

    # 5. Tag Confidence (A+, A, A-, B+ based on score percentile)
    score_cutoffs = np.percentile(top30['HR_Score'], [90, 75, 60])
    conditions = [
        (top30['HR_Score'] >= score_cutoffs[0]),
        (top30['HR_Score'] >= score_cutoffs[1]),
        (top30['HR_Score'] >= score_cutoffs[2])
    ]
    choices = ['A+', 'A', 'A-']
    top30['Confidence'] = np.select(conditions, choices, default='B+')

    # 6. Output to CSV
    today = date.today().isoformat()
    output_dir = 'data/output'
    os.makedirs(output_dir, exist_ok=True)

    # Save full details for internal use
    top30.to_csv(f'{output_dir}/apex_top30_full_{today}.csv', index=False)
    
    # Save simplified version for distribution
    top30[['Player', 'Team', 'Opponent', 'HR_Score', 'Confidence']].to_csv(
        f'{output_dir}/apex_top30_{today}.csv', index=False
    )
    
    # Save latest version (overwrite daily)
    top30[['Player', 'Team', 'Opponent', 'HR_Score', 'Confidence']].to_csv(
        f'{output_dir}/apex_top30_latest.csv', index=False
    )

    print(f">> Top 30 HR Predictions saved to {output_dir}/apex_top30_{today}.csv")
    return top30
