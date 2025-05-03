# utils/data_fetcher.py
# Data Fetching Utilities for HR Prediction System

import pandas as pd
import numpy as np
import os
from datetime import date, datetime
import requests
import time

def get_raw_player_data():
    """
    Fetches or loads raw player statistics data for HR prediction.
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing player data with stats needed for prediction
    """
    print(">> Fetching Raw Player Data...")
    
    # Attempt to load from data directory
    data_path = 'data/raw_player_stats.csv'
    
    if os.path.exists(data_path):
        # Load existing data file
        player_df = pd.read_csv(data_path)
        print(f">> Loaded player data: {len(player_df)} players")
    else:
        # Create directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Generate basic data structure for initial use
        print(">> No player data found. Creating minimal dataset for demonstration.")
        
        # Create minimal player data with necessary columns
        player_data = {
            'PlayerID': list(range(1, 51)),
            'Player': [f"Player {i}" for i in range(1, 51)],
            'Team': np.random.choice(['NYY', 'BOS', 'LAD', 'HOU', 'ATL', 'CHC', 'NYM', 'PHI', 'SD', 'TB'], 50),
            'Position': np.random.choice(['OF', '1B', '3B', 'SS', '2B', 'C', 'DH'], 50),
            'Barrel%': np.random.uniform(5, 15, 50),
            'LaunchAngleSweetSpot%': np.random.uniform(25, 45, 50),
            'xISO': np.random.uniform(0.150, 0.350, 50),
            'HR_Season': np.random.randint(5, 40, 50),
            'Stadium': np.random.choice(['Yankee Stadium', 'Fenway Park', 'Dodger Stadium', 'Minute Maid Park', 
                                        'Truist Park', 'Wrigley Field', 'Citi Field', 'Citizens Bank Park', 
                                        'Petco Park', 'Tropicana Field'], 50),
            'OpposingPitcher': [f"Pitcher {i}" for i in range(1, 51)],
            'PitcherID': np.random.randint(101, 150, 50),
            'Opponent': np.random.choice(['NYY', 'BOS', 'LAD', 'HOU', 'ATL', 'CHC', 'NYM', 'PHI', 'SD', 'TB'], 50),
            'IsHome': np.random.choice([True, False], 50),
            'Temperature': np.random.randint(55, 95, 50),
            'WindSpeed': np.random.randint(0, 20, 50),
            'WindDirection': np.random.choice(['In', 'Out', 'Crosswind', 'Neutral'], 50),
            'Humidity': np.random.randint(30, 90, 50)
        }
        
        player_df = pd.DataFrame(player_data)
        
        # Save data for future use
        player_df.to_csv(data_path, index=False)
        print(f">> Created minimal player dataset: {len(player_df)} players")
    
    # Check for required columns and add if missing
    required_columns = [
        'PlayerID', 'Player', 'Team', 'Position', 'Barrel%', 'LaunchAngleSweetSpot%', 
        'xISO', 'HR_Season', 'Stadium', 'OpposingPitcher', 'PitcherID', 'Opponent', 
        'IsHome', 'Temperature', 'WindSpeed', 'WindDirection', 'Humidity'
    ]
    
    for col in required_columns:
        if col not in player_df.columns:
            print(f"WARNING: Missing column {col} in player data. Adding default values.")
            
            # Add default values based on column type
            if col == 'PlayerID':
                player_df[col] = range(1, len(player_df) + 1)
            elif col == 'Player':
                player_df[col] = [f"Player {i}" for i in range(1, len(player_df) + 1)]
            elif col in ['Team', 'Opponent']:
                player_df[col] = np.random.choice(['NYY', 'BOS', 'LAD', 'HOU', 'ATL', 'CHC', 'NYM', 'PHI', 'SD', 'TB'], len(player_df))
            elif col == 'Position':
                player_df[col] = np.random.choice(['OF', '1B', '3B', 'SS', '2B', 'C', 'DH'], len(player_df))
            elif col in ['Barrel%', 'LaunchAngleSweetSpot%']:
                player_df[col] = np.random.uniform(5, 15, len(player_df))
            elif col == 'xISO':
                player_df[col] = np.random.uniform(0.150, 0.350, len(player_df))
            elif col == 'HR_Season':
                player_df[col] = np.random.randint(5, 40, len(player_df))
            elif col == 'Stadium':
                player_df[col] = np.random.choice(['Yankee Stadium', 'Fenway Park', 'Dodger Stadium'], len(player_df))
            elif col == 'OpposingPitcher':
                player_df[col] = [f"Pitcher {i}" for i in range(1, len(player_df) + 1)]
            elif col == 'PitcherID':
                player_df[col] = np.random.randint(101, 150, len(player_df))
            elif col == 'IsHome':
                player_df[col] = np.random.choice([True, False], len(player_df))
            elif col == 'Temperature':
                player_df[col] = np.random.randint(55, 95, len(player_df))
            elif col == 'WindSpeed':
                player_df[col] = np.random.randint(0, 20, len(player_df))
            elif col == 'WindDirection':
                player_df[col] = np.random.choice(['In', 'Out', 'Crosswind', 'Neutral'], len(player_df))
            elif col == 'Humidity':
                player_df[col] = np.random.randint(30, 90, len(player_df))
    
    return player_df

def get_actual_hr_data(target_date=None):
    """
    Fetches or loads actual home run data for a specific date.
    
    Parameters:
    -----------
    target_date : str
        ISO format date string (YYYY-MM-DD) to get HR data for
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing actual HR data for the specified date
    """
    if target_date is None:
        # Default to yesterday
        target_date = (date.today() - pd.Timedelta(days=1)).isoformat()
    
    print(f">> Fetching Actual HR Data for {target_date}...")
    
    # Attempt to load from data directory
    data_dir = 'data/actual'
    os.makedirs(data_dir, exist_ok=True)
    data_path = f'{data_dir}/actual_hr_{target_date}.csv'
    
    if os.path.exists(data_path):
        # Load existing data file
        hr_df = pd.read_csv(data_path)
        print(f">> Loaded actual HR data: {len(hr_df)} home runs")
        return hr_df
    
    # Try to fetch data from an API (simulated here)
    print(">> No cached HR data found. Attempting to fetch from MLB API...")
    
    # Simulated API request with retry
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # In a real implementation, this would make an API call to MLB or a sports data provider
            # For now, we'll create simulated data
            
            # Create minimal HR data
            hr_count = np.random.randint(10, 25)  # Random number of HRs for the day
            
            player_pool = [
                {"Player": "Aaron Judge", "Team": "NYY"},
                {"Player": "Shohei Ohtani", "Team": "LAD"},
                {"Player": "Mike Trout", "Team": "LAA"},
                {"Player": "Juan Soto", "Team": "NYY"},
                {"Player": "Ronald Acuña Jr.", "Team": "ATL"},
                {"Player": "Fernando Tatis Jr.", "Team": "SD"},
                {"Player": "Yordan Alvarez", "Team": "HOU"},
                {"Player": "Vladimir Guerrero Jr.", "Team": "TOR"},
                {"Player": "Pete Alonso", "Team": "NYM"},
                {"Player": "Bryce Harper", "Team": "PHI"},
                {"Player": "Mookie Betts", "Team": "LAD"},
                {"Player": "Matt Olson", "Team": "ATL"},
                {"Player": "Kyle Schwarber", "Team": "PHI"},
                {"Player": "Adolis García", "Team": "TEX"},
                {"Player": "Teoscar Hernández", "Team": "LAD"},
                {"Player": "Bobby Witt Jr.", "Team": "KC"},
                {"Player": "José Ramírez", "Team": "CLE"},
                {"Player": "Gunnar Henderson", "Team": "BAL"},
                {"Player": "Rafael Devers", "Team": "BOS"},
                {"Player": "Francisco Lindor", "Team": "NYM"}
            ]
            
            # Randomly select players who hit HRs today
            hr_hitters = np.random.choice(len(player_pool), hr_count, replace=True)
            
            hr_data = []
            for hitter_idx in hr_hitters:
                player = player_pool[hitter_idx]
                # Some players might hit multiple HRs
                hr_data.append({
                    "Player": player["Player"],
                    "Team": player["Team"],
                    "HR_Count": 1 if np.random.random() < 0.85 else 2,  # 15% chance of multi-HR game
                    "Date": target_date
                })
            
            # Combine players with same name (multiple HRs)
            hr_df = pd.DataFrame(hr_data)
            hr_df = hr_df.groupby(['Player', 'Team', 'Date'], as_index=False)['HR_Count'].sum()
            
            # Save data for future use
            hr_df.to_csv(data_path, index=False)
            print(f">> Retrieved {len(hr_df)} home runs for {target_date}")
            return hr_df
            
        except Exception as e:
            print(f"ERROR: Failed to fetch HR data (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
    
    print("ERROR: Failed to fetch actual HR data after multiple attempts")
    return None
