# Apex Arc Master: MLB Home Run Prediction System

A sophisticated MLB home run prediction system that generates daily player rankings and parlay combinations with automated performance tracking and diagnostic alerts.

## Overview

Apex Arc Master uses a multi-factor approach to predict which MLB players are most likely to hit home runs on a given day. The system:

1. Analyzes player-specific factors (barrel%, launch angle, ISO)
2. Evaluates contextual factors (weather, ballpark, opposing pitcher)
3. Generates probability-ranked list of the top 30 HR candidates
4. Creates optimal parlay stack combinations
5. Tracks prediction performance against actual results
6. Provides diagnostic alerts when performance drops below thresholds

## System Components

- **Models**: Core prediction algorithms and parlay stack builder
- **Overlays**: Contextual factors that modify base HR probabilities
  - Weather Impact (temperature, wind, humidity)
  - Park Factors (stadium-specific HR tendencies)
  - Pitcher Matchups (HR/9, hard hit rate, K%)
  - Batter Form (recent performance, hot streaks)
- **Trackers**: Performance evaluation and diagnostics
- **Utils**: Data fetching and utility functions

## Daily Simulation Workflow

The system runs a daily workflow that:

1. Generates top 30 HR predictions with confidence ratings
2. Builds HR parlay stacks for optimal combinations
3. Tracks hits, misses, and surprises compared to actual results
4. Runs shadow diagnostics to evaluate prediction performance
5. Triggers alerts if performance drops below thresholds

## Output Files

- `data/output/apex_top30_YYYY-MM-DD.csv`: Daily top 30 HR predictions
- `data/output/apex_parlays_YYYY-MM-DD.csv`: Daily optimal parlay combinations
- `data/output/tracking/tracking_YYYY-MM-DD.csv`: Daily tracking results
- `data/output/diagnostics/diagnostic_report_YYYY-MM-DD.csv`: Daily diagnostics report

## Tech Stack

- Python
- Pandas
- NumPy

## Usage

To run the daily simulation:

```
python run_daily_simulation.py
```