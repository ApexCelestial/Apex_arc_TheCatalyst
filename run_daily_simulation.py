# run_daily_simulation.py
# Apex Arc Master Daily Simulation Runner

from models.top30_hr_predictor import generate_top30_predictions
from models.parlay_stack_builder import build_parlay_stacks
from trackers.hr_tracker import track_home_runs
from trackers.shadow_diagnostics import run_shadow_diagnostics

def run_daily_simulation():
    """
    Master runner that executes the complete daily workflow:
    1. Generate top 30 HR predictions
    2. Build HR parlay stacks
    3. Track today's home runs
    4. Run diagnostics on yesterday's results
    """
    print(">> Running Apex Arc Daily Simulation...")

    # Step 1: Generate Top 30 HR Predictions
    top30 = generate_top30_predictions()

    # Step 2: Build HR Parlay Stacks
    parlays = build_parlay_stacks()

    # Step 3: Track Today's Home Runs (postgame)
    tracking = track_home_runs()

    # Step 4: Run Diagnostics on Yesterday's Results
    diagnostics = run_shadow_diagnostics()

    print(">> Daily Simulation Complete.")
    
    return {
        "predictions": top30,
        "parlays": parlays,
        "tracking": tracking,
        "diagnostics": diagnostics
    }

if __name__ == "__main__":
    run_daily_simulation()
