# File: modules/insightcloud/analytics.py
# This is the final, definitive version with robust data preparation.

import pandas as pd
import json
import logging
from typing import List, Dict
from sklearn.ensemble import IsolationForest

from memorycore.memory_manager import get_memory_core

# Use a logger for cleaner, more professional output
logger = logging.getLogger(__name__)

# This is the in-memory cache that powers all the fast analytics.
DATA_CACHE: pd.DataFrame = pd.DataFrame()


async def refresh_data_cache() -> bool:
    """
    Fetches events from MemoryCore, processes them into a clean DataFrame,
    and correctly sets a DatetimeIndex for reliable time-series analysis.
    """
    global DATA_CACHE
    try:
        # 1. Fetch raw event rows from MemoryCore. This logic is unchanged.
        all_events_rows = get_memory_core().structured.get_recent_events(n=2000) # Increased limit slightly
        
        if not all_events_rows:
            logger.info("[Analytics] No events found in MemoryCore. Cache is empty.")
            DATA_CACHE = pd.DataFrame()
            return True

        # 2. Convert to a list of standard dictionaries. This logic is unchanged.
        all_events = [dict(row) for row in all_events_rows]

        # 3. Create the initial pandas DataFrame. This logic is unchanged.
        df = pd.DataFrame(all_events)
        
        # --- THIS IS THE DEFINITIVE FIX ---
        # The TypeError occurs because the 'timestamp' column is not the index when
        # .resample() is called. This block fixes that permanently.

        # 4a. Convert the 'timestamp' column to proper datetime objects.
        #     `errors='coerce'` will turn any unparseable timestamps into `NaT` (Not a Time).
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

        # 4b. Remove any rows that had an unparseable timestamp.
        df.dropna(subset=['timestamp'], inplace=True)

        # 4c. Set this now-guaranteed-to-be-datetime column as the DataFrame's index.
        #     This is the critical step that makes `.resample()` work.
        df.set_index('timestamp', inplace=True)
        # --- END OF THE DEFINITIVE FIX ---
        
        # 5. Robustly parse the 'details' JSON string. This logic is unchanged.
        try:
            details_df = pd.json_normalize(df['details'].apply(json.loads))
            # Important: ensure the new details DataFrame shares the same DatetimeIndex
            details_df.index = df.index
            df = pd.concat([df.drop('details', axis=1), details_df], axis=1)
        except (TypeError, json.JSONDecodeError) as e:
            logger.warning(f"[Analytics] Could not parse all 'details' JSON fields: {e}")

        DATA_CACHE = df
        logger.info(f"[Analytics] Data cache refreshed successfully with {len(DATA_CACHE)} events.")
        return True
    except Exception as e:
        logger.error(f"[Analytics] FATAL: Failed to refresh data cache: {e}", exc_info=True)
        return False


def get_events_per_day() -> Dict:
    """Aggregates event counts by day using the now-correct DatetimeIndex."""
    if DATA_CACHE.empty: return {}
    # This line will now work correctly because the DATA_CACHE has a DatetimeIndex.
    events_by_day = DATA_CACHE.resample('D').size()
    return {timestamp.strftime('%Y-%m-%d'): count for timestamp, count in events_by_day.items()}


def get_events_by_module() -> Dict:
    """Groups event counts by the source module."""
    if DATA_CACHE.empty: return {}
    # This function works on a column, so it was already correct and is unchanged.
    return DATA_CACHE.groupby('source')['id'].count().to_dict()


def find_anomalies() -> List[Dict]:
    """Uses IsolationForest to detect anomalous spikes in event frequency."""
    if DATA_CACHE.empty or len(DATA_CACHE) < 10:
        return [{"message": "Not enough data for anomaly detection."}]
    
    # This line will now work correctly because the DATA_CACHE has a DatetimeIndex.
    events_per_hour = DATA_CACHE.resample('h').size().reset_index()
    events_per_hour.columns = ['timestamp', 'count']
    
    if len(events_per_hour) < 2: return []
    
    model = IsolationForest(contamination=0.1, random_state=42)
    events_per_hour['anomaly'] = model.fit_predict(events_per_hour[['count']])
    
    anomalies = events_per_hour[events_per_hour['anomaly'] == -1]
    
    return [{
        "timestamp_hour": row['timestamp'].isoformat(),
        "event_count": int(row['count']),
        "details": "Unusually high number of events detected in this hour."
    } for _, row in anomalies.iterrows()]