# trackers/shadow_diagnostics.py
# Shadow Diagnostics for Performance Evaluation

import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def run_shadow_diagnostics():
    """
    Runs diagnostics on recent prediction performance.
    Evaluates hit rates, missed predictions, and surprise events.
    Triggers alerts if performance falls below thresholds.
    """
    
    print(">> Running Shadow Diagnostics...")
    
    # Get recent dates for analysis (last 7 days)
    today = date.today()
    last_week = [(today - timedelta(days=i)).isoformat() for i in range(1, 8)]
    
    # Paths for tracking files
    tracking_dir = 'data/output/tracking'
    
    # Check if tracking directory exists
    if not os.path.exists(tracking_dir):
        print(f"ERROR: Tracking directory {tracking_dir} not found.")
        return None
    
    # Load recent tracking data
    tracking_files = [f'{tracking_dir}/tracking_{day}.csv' for day in last_week]
    tracking_data = []
    
    for file in tracking_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            tracking_data.append(df)
    
    if not tracking_data:
        print("WARNING: No tracking data found for the past week.")
        return None
    
    # Combine all tracking data
    combined_df = pd.concat(tracking_data, ignore_index=True)
    
    # Calculate diagnostics
    hit_count = len(combined_df[combined_df['Result'] == 'Hit'])
    miss_count = len(combined_df[combined_df['Result'] == 'Miss'])
    surprise_count = len(combined_df[combined_df['Result'] == 'Surprise'])
    
    total_predictions = hit_count + miss_count
    total_hrs = hit_count + surprise_count
    
    hit_rate = hit_count / total_predictions if total_predictions > 0 else 0
    surprise_rate = surprise_count / total_hrs if total_hrs > 0 else 0
    
    # Confidence level performance
    confidence_performance = combined_df[combined_df['Result'] != 'Surprise'].groupby('Confidence')['Result'].apply(
        lambda x: (x == 'Hit').mean()
    ).reset_index()
    confidence_performance.columns = ['Confidence', 'Success_Rate']
    
    # Team performance
    team_performance = combined_df[combined_df['Result'] != 'Surprise'].groupby('Team')['Result'].apply(
        lambda x: (x == 'Hit').mean()
    ).reset_index()
    team_performance.columns = ['Team', 'Success_Rate']
    team_performance = team_performance.sort_values('Success_Rate', ascending=False)
    
    # Define alert thresholds
    hit_rate_threshold = 0.20  # At least 20% hit rate expected
    surprise_rate_threshold = 0.50  # No more than 50% surprises
    
    # Prepare diagnostic report
    diagnostic_report = {
        'Date': today.isoformat(),
        'Days_Analyzed': len(tracking_data),
        'Total_Predictions': total_predictions,
        'Hit_Count': hit_count,
        'Miss_Count': miss_count,
        'Surprise_Count': surprise_count,
        'Hit_Rate': hit_rate,
        'Surprise_Rate': surprise_rate,
        'Best_Team': team_performance.iloc[0]['Team'] if len(team_performance) > 0 else 'N/A',
        'Best_Team_Rate': team_performance.iloc[0]['Success_Rate'] if len(team_performance) > 0 else 0,
        'Worst_Team': team_performance.iloc[-1]['Team'] if len(team_performance) > 0 else 'N/A',
        'Worst_Team_Rate': team_performance.iloc[-1]['Success_Rate'] if len(team_performance) > 0 else 0,
        'A+_Performance': confidence_performance[confidence_performance['Confidence'] == 'A+']['Success_Rate'].values[0] 
                          if 'A+' in confidence_performance['Confidence'].values else 0,
        'Hit_Rate_Alert': hit_rate < hit_rate_threshold,
        'Surprise_Rate_Alert': surprise_rate > surprise_rate_threshold
    }
    
    # Save diagnostic report
    output_dir = 'data/output/diagnostics'
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to DataFrame and save
    report_df = pd.DataFrame([diagnostic_report])
    report_df.to_csv(f'{output_dir}/diagnostic_report_{today.isoformat()}.csv', index=False)
    
    # Send alerts if thresholds are exceeded
    alerts = []
    
    if hit_rate < hit_rate_threshold:
        alerts.append(f"WARNING: Hit rate ({hit_rate:.2f}) below threshold ({hit_rate_threshold})")
    
    if surprise_rate > surprise_rate_threshold:
        alerts.append(f"WARNING: Surprise rate ({surprise_rate:.2f}) above threshold ({surprise_rate_threshold})")
    
    # Log alerts
    if alerts:
        alert_file = f'{output_dir}/alerts.log'
        with open(alert_file, 'a') as f:
            for alert in alerts:
                f.write(f"{today.isoformat()}: {alert}\n")
        
        # Send email alert if environment variable is set
        send_email_alerts(alerts, diagnostic_report)
    
    print(f">> Diagnostics Complete: Hit Rate = {hit_rate:.2f}, Surprise Rate = {surprise_rate:.2f}")
    print(f">> Report saved to {output_dir}/diagnostic_report_{today.isoformat()}.csv")
    
    if alerts:
        print(">> ALERTS TRIGGERED:")
        for alert in alerts:
            print(f"   {alert}")
    
    return diagnostic_report

def send_email_alerts(alerts, diagnostic_report):
    """
    Sends email alerts when thresholds are exceeded.
    Requires email configuration via environment variables.
    """
    # Get email settings from environment variables
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    alert_recipient = os.getenv('ALERT_EMAIL')
    
    # Skip if email configuration is missing
    if not all([smtp_server, smtp_port, smtp_username, smtp_password, alert_recipient]):
        print("WARNING: Email configuration incomplete. Skipping email alerts.")
        return
    
    # Compose email
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = alert_recipient
    msg['Subject'] = f"ALERT: MLB HR Prediction System - {len(alerts)} Alerts Triggered"
    
    # Email body
    body = "The following alerts have been triggered:\n\n"
    for alert in alerts:
        body += f"- {alert}\n"
    
    body += "\n\nDiagnostic Summary:\n"
    body += f"- Date: {diagnostic_report['Date']}\n"
    body += f"- Days Analyzed: {diagnostic_report['Days_Analyzed']}\n"
    body += f"- Hit Rate: {diagnostic_report['Hit_Rate']:.2f}\n"
    body += f"- Surprise Rate: {diagnostic_report['Surprise_Rate']:.2f}\n"
    body += f"- Total Predictions: {diagnostic_report['Total_Predictions']}\n"
    body += f"- Hit Count: {diagnostic_report['Hit_Count']}\n"
    body += f"- Miss Count: {diagnostic_report['Miss_Count']}\n"
    body += f"- Surprise Count: {diagnostic_report['Surprise_Count']}\n"
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f">> Email alert sent to {alert_recipient}")
    except Exception as e:
        print(f"ERROR: Failed to send email alert: {e}")
