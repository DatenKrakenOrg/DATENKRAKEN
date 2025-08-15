import pandas as pd
from datetime import timedelta
import pytz
import numpy as np

CSV_FILE_NAME = "postgres_start_times.csv"

def calculate_uptime_stats():
    # Load and preprocess data
    df = pd.read_csv(CSV_FILE_NAME, dtype={'postgres_start_time': np.int64, 'recorded_time': np.int64})
    df['recorded'] = pd.to_datetime(df['recorded_time'], unit='s', utc=True)
    df['start'] = pd.to_datetime(df['postgres_start_time'], unit='s', utc=True)
    
    # Convert to local timezone
    local_tz = pytz.timezone('Europe/Berlin')
    df['recorded_local'] = df['recorded'].dt.tz_convert(local_tz)
    df['start_local'] = df['start'].dt.tz_convert(local_tz)
    
  # Analysis period
    newest_time = df['recorded_local'].max()
    start_of_week = (newest_time - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    df_week = df[df['recorded_local'] >= start_of_week].sort_values('recorded_local')
    
    # Calculate downtime
    total_downtime = timedelta(0)
    failure_start = None
    
    for idx, row in df_week.iterrows():
        if row['postgres_start_time'] == 0:
            if failure_start is None:
                failure_start = row['recorded_local']
        else:
            if failure_start is not None:
                total_downtime += row['recorded_local'] - failure_start
                failure_start = None
    
    # Handle ongoing downtime at end
    if failure_start is not None:
        total_downtime += newest_time - failure_start
    
    # Calculate statistics
    total_time = newest_time - start_of_week
    uptime_percentage = ((total_time - total_downtime).total_seconds() / total_time.total_seconds()) * 100
    
    print("\n=== Accurate Uptime Analysis ===")
    print(f"Analysis period: {start_of_week} to {newest_time}")
    print(f"Total time: {total_time}")
    print(f"Total downtime: {total_downtime}")
    print(f"Uptime percentage: {uptime_percentage:.2f}%")

calculate_uptime_stats()

