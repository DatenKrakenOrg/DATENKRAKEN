import pandas as pd
from datetime import datetime, timedelta
import pytz
import numpy as np

CSV_FILE_NAME="postgres_start_times.csv"

def calculate_uptime_stats():
    try:
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
        
        # Get current time
        current_time = datetime.now(local_tz)
        
        # Get start of current week (Monday)
        start_of_week = current_time - timedelta(days=current_time.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        print("Calculating uptime...")
        # Initialize totals
        elapsed_uptime = timedelta(0)
        elapsed_total = timedelta(0)
        
        results = []
        for day in range(7):
            day_start = start_of_week + timedelta(days=day)
            day_end = day_start + timedelta(days=1)
            
            # Skip future days
            if day_start > current_time:
                results.append({
                    'date': day_start.date(),
                    'day': day_start.strftime('%A'),
                    'uptime': timedelta(0),
                    'downtime': timedelta(0),
                    'availability': 0.0,
                    'status': 'Future'
                })
                continue
                
            # For current day, only count up to current time
            if day_end > current_time:
                day_end = current_time
                day_status = 'Partial'
            else:
                day_status = 'Complete'
            
            day_duration = day_end - day_start
            elapsed_total += day_duration
            
            # Filter events for this day
            day_mask = ((df['recorded_local'] >= day_start) & 
                       (df['start_local'] < day_end))
            day_events = df[day_mask].sort_values('start_local')
            
            # Calculate uptime for this day
            day_uptime = timedelta(0)
            coverage_start = day_start
            
            for _, row in day_events.iterrows():
                if row['start_local'] < row['recorded_local']:
                    period_start = max(row['start_local'], coverage_start)
                    period_end = min(row['recorded_local'], day_end)
                    
                    if period_start < period_end:
                        uptime_period = period_end - period_start
                        day_uptime += uptime_period
                        coverage_start = period_end
            
            elapsed_uptime += day_uptime
            
            # Calculate daily availability
            day_availability = (day_uptime.total_seconds() / day_duration.total_seconds() * 100 
                              if day_duration.total_seconds() > 0 else 0.0)
            
            results.append({
                'date': day_start.date(),
                'day': day_start.strftime('%A'),
                'uptime': day_uptime,
                'downtime': day_duration - day_uptime,
                'availability': day_availability,
                'status': day_status
            })
        
        # Calculate weekly availability (only elapsed time)
        weekly_availability = (elapsed_uptime.total_seconds() / elapsed_total.total_seconds() * 100
                             if elapsed_total.total_seconds() > 0 else 0.0)
        
        return pd.DataFrame(results), weekly_availability
    
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame(), 0.0

if __name__ == "__main__":
    print("Calculating PostgreSQL uptime statistics...")
    start_time = datetime.now()
    
    uptime_df, weekly_uptime_pct = calculate_uptime_stats()
    
    if not uptime_df.empty:
        print("\nDaily Uptime Report (Local Time):")
        print(uptime_df.to_string(
            columns=['date', 'day', 'uptime', 'downtime', 'availability', 'status'],
            formatters={
                'uptime': lambda x: str(x).split('.')[0],
                'downtime': lambda x: str(x).split('.')[0],
                'availability': '{:.2f}%'.format
            },
            index=False
        ))
        
        print(f"\nWeekly Uptime Percentage: {weekly_uptime_pct:.2f}% (of elapsed time)")
        print(f"Calculation completed in {datetime.now() - start_time}")
    else:
        print("No results could be calculated.")
