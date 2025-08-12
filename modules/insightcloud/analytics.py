# File: modules/insightcloud/analytics.py

import pandas as pd
import json
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest

from memorycore.memory_manager import get_memory_core

# In-memory cache to hold the last 24 hours of data for fast responses
DATA_CACHE: pd.DataFrame = pd.DataFrame()

async def refresh_data_cache() -> bool:
    """
    Fetches recent structured events from MemoryCore and populates the
    in-memory pandas DataFrame cache for fast analytical queries.
    """
    global DATA_CACHE
    try:
        # 1. Fetch raw event rows from the correct structured memory backend
        all_events_rows = get_memory_core().structured.get_recent_events(n=1000)
        
        if not all_events_rows:
            print("[Analytics] No events found in MemoryCore to build cache.")
            DATA_CACHE = pd.DataFrame() # Ensure cache is empty
            return True

        # 2. Convert sqlite3.Row objects to a list of standard dictionaries
        all_events = [dict(row) for row in all_events_rows]

        # 3. Create a powerful pandas DataFrame
        df = pd.DataFrame(all_events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 4. Robustly parse the 'details' JSON string into separate columns
        # This "flattens" the data, making it much easier to analyze
        try:
            # Use json_normalize which is perfect for nested JSON
            details_df = pd.json_normalize(df['details'].apply(json.loads))
            # Combine the flattened details with the main DataFrame
            df = pd.concat([df.drop('details', axis=1), details_df], axis=1)
        except (TypeError, json.JSONDecodeError):
            print("[Analytics] Warning: Could not parse all 'details' fields into columns.")


        DATA_CACHE = df
        print(f"[Analytics] Data cache refreshed successfully with {len(DATA_CACHE)} events.")
        return True
    except Exception as e:
        print(f"[Analytics] ERROR: Failed to refresh data cache. {e}", exc_info=True)
        return False

def get_events_per_day() -> Dict:
    """Aggregates event counts by day."""
    if DATA_CACHE.empty: return {}
    events_by_day = DATA_CACHE.set_index('timestamp').resample('D').size()
    # Format for clean JSON output
    return {timestamp.strftime('%Y-%m-%d'): count for timestamp, count in events_by_day.items()}

def get_events_by_module() -> Dict:
    """Groups event counts by the source module."""
    if DATA_CACHE.empty: return {}
    return DATA_CACHE.groupby('source')['id'].count().to_dict()

def find_anomalies() -> List[Dict]:
    """Uses IsolationForest to detect anomalous spikes in event frequency."""
    if DATA_CACHE.empty or len(DATA_CACHE) < 10:
        return [{"message": "Not enough data to perform anomaly detection."}]
    
    events_per_hour = DATA_CACHE.set_index('timestamp').resample('h').size().reset_index(name='count')
    if len(events_per_hour) < 2: return [] # Need at least 2 data points

    model = IsolationForest(contamination=0.1, random_state=42) # Assume up to 10% are anomalies
    events_per_hour['anomaly'] = model.fit_predict(events_per_hour[['count']])
    
    anomalies = events_per_hour[events_per_hour['anomaly'] == -1]
    
    return [{
        "timestamp_hour": row['timestamp'].isoformat(),
        "event_count": int(row['count']),
        "details": "Unusually high number of events detected in this hour."
    } for _, row in anomalies.iterrows()]