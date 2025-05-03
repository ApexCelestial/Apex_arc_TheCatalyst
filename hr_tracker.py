# trackers/hr_tracker.py
# Home Run Tracker for Performance Analysis

import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
from utils.data_fetcher import get_actual_hr_data

def track_home_runs():
    """
    Tracks actual home runs hit and compares them against predictions.
    Categorizes results as Hits (predicted correctly), Misses (predicted but didn't hit), 
    and Surprises (hit HR but wasn't predicted).
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with tracking results
    """
    
    print(">> Tracking Today's Home Runs...")
    
    # Get yesterday's date (since we're tracking completed games)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    # Paths for prediction and results files
    output_dir = 'data/output'
    prediction_file = f'{output_dir}/apex_top30_{yesterday}.csv'
    tracking_dir = f'{output_dir}/tracking'
    
    # Create tracking directory if it doesn't exist
    os.makedirs(tracking_dir, exist_ok=True)
    
    # Check if the prediction file exists
    if not os.path.exists(prediction_file):
        print(f"WARNING: Prediction file {prediction_file} not found. Trying latest predictions...")
        prediction_file = f'{output_dir}/apex_top30_latest.csv'
        if not os.path.exists(prediction_file):
            print("ERROR: No prediction file found. Cannot track home runs.")
            return None
    
    # Load predictions
    predictions = pd.read_csv(prediction_file)
    
    # Get actual HR data from the data fetcher
    actual_hr_data = get_actual_hr_data(yesterday)
    
    if actual_hr_data is None or len(actual_hr_data) == 0:
        print(f"WARNING: No actual HR data available for {yesterday}")
        return None
    
    # Initialize tracking results
    tracking_results = []
    
    # Process hits (correctly predicted HRs)
    hits = pd.merge(
        predictions,
        actual_hr_data,
        on='Player',
        how='inner'
    )
    
    for _, hit in hits.iterrows():
        tracking_results.append({
            'Date': yesterday,
            'Player': hit['Player'],
            'Team': hit['Team_x'],  # Use team from predictions
            'HR_Score': hit['HR_Score'],
            'Confidence': hit['Confidence'],
            'Actual_HR': hit['HR_Count'],
            'Result': 'Hit',
            'Multiple_HR': hit['HR_Count'] > 1
        })
    
    # Process misses (predicted but didn't hit)
    misses = pd.merge(
        predictions,
        actual_hr_data,
        on='Player',
        how='left',
        indicator=True
    )
    misses = misses[misses['_merge'] == 'left_only']
    
    for _, miss in misses.iterrows():
        # Get the columns that actually exist in miss
        player = miss['Player']
        team = miss['Team'] if 'Team' in miss else 'Unknown'
        hr_score = miss['HR_Score'] if 'HR_Score' in miss else 0
        confidence = miss['Confidence'] if 'Confidence' in miss else 'None'
        
        tracking_results.append({
            'Date': yesterday,
            'Player': player,
            'Team': team,
            'HR_Score': hr_score,
            'Confidence': confidence,
            'Actual_HR': 0,
            'Result': 'Miss',
            'Multiple_HR': False
        })
    
    # Process surprises (hit HR but wasn't predicted)
    surprises = pd.merge(
        actual_hr_data,
        predictions,
        on='Player',
        how='left',
        indicator=True
    )
    surprises = surprises[surprises['_merge'] == 'left_only']
    
    for _, surprise in surprises.iterrows():
        # Check which Team column exists (_x suffix might not be there)
        team_col = 'Team_x' if 'Team_x' in surprise else 'Team'
        
        tracking_results.append({
            'Date': yesterday,
            'Player': surprise['Player'],
            'Team': surprise[team_col] if team_col in surprise else 'Unknown',
            'HR_Score': 0,  # Wasn't predicted
            'Confidence': 'None',
            'Actual_HR': surprise['HR_Count'] if 'HR_Count' in surprise else 1,
            'Result': 'Surprise',
            'Multiple_HR': surprise['HR_Count'] > 1 if 'HR_Count' in surprise else False
        })
    
    # Convert to DataFrame
    tracking_df = pd.DataFrame(tracking_results)
    
    # Save tracking results
    tracking_df.to_csv(f'{tracking_dir}/tracking_{yesterday}.csv', index=False)
    
    # Update cumulative tracking file
    cumulative_file = f'{tracking_dir}/cumulative_tracking.csv'
    if os.path.exists(cumulative_file):
        cumulative_df = pd.read_csv(cumulative_file)
        # Append new results
        cumulative_df = pd.concat([cumulative_df, tracking_df], ignore_index=True)
    else:
        cumulative_df = tracking_df
    
    # Save cumulative results
    cumulative_df.to_csv(cumulative_file, index=False)
    
    # Generate summary statistics
    hit_rate = len(hits) / len(predictions) if len(predictions) > 0 else 0
    surprise_rate = len(surprises) / (len(hits) + len(surprises)) if (len(hits) + len(surprises)) > 0 else 0
    
    print(f">> Tracking Complete: Hit Rate = {hit_rate:.2f}, Surprise Rate = {surprise_rate:.2f}")
    print(f">> Results saved to {tracking_dir}/tracking_{yesterday}.csv")
    
    return tracking_df
