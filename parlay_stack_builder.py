# models/parlay_stack_builder.py
# Parlay Stack Builder for HR Predictions

import pandas as pd
import numpy as np
import os
from datetime import date
from itertools import combinations

def build_parlay_stacks():
    """
    Builds optimal parlay stack combinations from the top HR predictions.
    Creates 2-player combinations prioritizing high confidence and minimizing correlation.
    """
    print(">> Building HR Parlay Stacks...")

    today = date.today().isoformat()
    output_dir = 'data/output'
    input_file = f'{output_dir}/apex_top30_full_{today}.csv'
    
    # Check if the predictions file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Prediction file {input_file} not found.")
        return None
    
    # Load the top 30 predictions with full details
    top30 = pd.read_csv(input_file)
    
    # Create all possible 2-player combinations from top 20 players
    top20 = top30.head(20)
    player_combos = list(combinations(top20.index, 2))
    
    stacks = []
    for combo in player_combos:
        player1 = top20.iloc[combo[0]]
        player2 = top20.iloc[combo[1]]
        
        # Skip players from same team (highly correlated)
        if player1['Team'] == player2['Team']:
            continue
            
        # Calculate combined score with a slight discount for correlation
        # Convert confidence ratings to numeric bonuses
        confidence_value = {
            'A+': 0.15, 
            'A': 0.10, 
            'A-': 0.05, 
            'B+': 0.0
        }
        
        # Calculate base score (product of individual probabilities)
        combo_score = player1['HR_Score'] * player2['HR_Score']
        
        # Apply confidence bonus
        combo_score *= (1 + confidence_value[player1['Confidence']] + confidence_value[player2['Confidence']])
        
        stacks.append({
            'Player1': player1['Player'],
            'Team1': player1['Team'],
            'Player2': player2['Player'],
            'Team2': player2['Team'],
            'Combined_Score': combo_score,
            'Player1_Confidence': player1['Confidence'],
            'Player2_Confidence': player2['Confidence']
        })
    
    # Convert to DataFrame and sort by score
    stacks_df = pd.DataFrame(stacks)
    stacks_df = stacks_df.sort_values('Combined_Score', ascending=False)
    
    # Take top 15 parlay combinations
    top_stacks = stacks_df.head(15)
    
    # Save to CSV
    os.makedirs(output_dir, exist_ok=True)
    top_stacks.to_csv(f'{output_dir}/apex_parlays_{today}.csv', index=False)
    top_stacks.to_csv(f'{output_dir}/apex_parlays_latest.csv', index=False)
    
    print(f">> Top Parlay Stacks saved to {output_dir}/apex_parlays_{today}.csv")
    return top_stacks
