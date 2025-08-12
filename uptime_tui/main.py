import pandas as pd
from datetime import datetime, timedelta
import pytz
import numpy as np

CSV_FILE_NAME = "postgres_start_times.csv"

def calculate_uptime_stats():
    print("Loading data...")
    # Load data with optimized parsing
    df = pd.read_csv(CSV_FILE_NAME, 
                    dtype={'postgres_start_time': np.int64, 'recorded_time': np.int64})
    
    print("Converting timestamps...")
    # Vectorized timestamp conversion
    df['start'] = pd.to_datetime(df['postgres_start_time'], unit='s', utc=True)
    df['recorded'] = pd.to_datetime(df['recorded_time'], unit='s', utc=True)
    
    # Convert to local timezone (UTC+2)
    local_tz = pytz.timezone('Europe/Berlin')
    df['start_local'] = df['start'].dt.tz_convert(local_tz)
    df['recorded_local'] = df['recorded'].dt.tz_convert(local_tz)
    
    # Get newest time from the file
    newest_time = df['recorded_local'].max()
    
    # Get start of current week (Monday)
    start_of_week = newest_time - timedelta(days=7)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    

    print(start_of_week, newest_time)
    print()
    uptime = df['recorded_local'] - df['start_local']
    df_week = df[df['recorded_local'] >= start_of_week]

    downtime_count = (df_week['postgres_start_time'] == 0).sum()

    totaltime = newest_time - start_of_week
    total_downtime = timedelta(0)
    # Iterate through records to compute downtime
    prev_time = start_of_week
    for idx, row in df_week.iterrows():
        current_time = row['recorded_local']
        time_since_prev = current_time - prev_time

        # If DB was down, add the entire interval since last check
        if row['postgres_start_time'] == 0:
            total_downtime += time_since_prev

        prev_time = current_time

    # Calculate uptime
    total_uptime = totaltime - total_downtime
    uptime_percentage = (total_uptime.total_seconds() / totaltime.total_seconds()) * 100

    print("\n--- Results ---")
    print(f"Analysis period: {start_of_week} to {newest_time}")
    print(f"Total time: {totaltime}")
    print(f"Total downtime: {total_downtime}")
    print(f"Uptime percentage: {uptime_percentage:.2f}%")

calculate_uptime_stats()
