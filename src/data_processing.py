import pandas as pd
import numpy as np
import sqlite3
import os

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROC_DIR = os.path.join(DATA_DIR, 'processed')

def process_events():
    print("Loading events...")
    events_path = os.path.join(RAW_DIR, 'events.csv')
    df = pd.read_csv(events_path)
    
    print("Parsing timestamps...")
    # Parse timestamps as Unix milliseconds
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    print("Deriving sessions...")
    df = df.sort_values(['visitorid', 'timestamp']).reset_index(drop=True)
    
    # Gaps > 30 mins
    df['time_diff'] = df.groupby('visitorid')['timestamp'].diff()
    # 30 mins = 30 * 60 * 1000 = 1800000 ms
    df['new_session'] = (df['time_diff'] > 1800000) | df['time_diff'].isna()
    df['session_id'] = df.groupby('visitorid')['new_session'].cumsum()
    df['session_uid'] = df['visitorid'].astype(str) + "_" + df['session_id'].astype(str)
    
    print("Loading and filtering item properties (categoryid)...")
    # Read property files in chunks
    cat_chunks = []
    for part in ['item_properties_part1.csv', 'item_properties_part2.csv']:
        path = os.path.join(RAW_DIR, part)
        for chunk in pd.read_csv(path, chunksize=1000000):
            # keep only categoryid
            cat_chunk = chunk[chunk['property'] == 'categoryid'].copy()
            cat_chunks.append(cat_chunk)
            
    cat_df = pd.concat(cat_chunks, ignore_index=True)
    cat_df['value'] = pd.to_numeric(cat_df['value'], errors='coerce')
    cat_df = cat_df.dropna(subset=['value'])
    cat_df['value'] = cat_df['value'].astype(int)
    cat_df.rename(columns={'value': 'categoryid'}, inplace=True)
    
    # Sort categories by timestamp to do as-of join
    cat_df = cat_df.sort_values('timestamp')
    df = df.sort_values('timestamp')
    
    print("Merging categories...")
    # Timestamp-aware join: find the latest categoryid for an itemid before the event timestamp
    # pandas merge_asof is perfect for this. Both need to be sorted by timestamp
    df = pd.merge_asof(
        df,
        cat_df[['timestamp', 'itemid', 'categoryid']],
        on='timestamp',
        by='itemid',
        direction='backward'
    )
    
    print("Aggregating sessions...")
    # Sessions aggregation
    # We will compute properties: view count, cart count, purchase count, elapsed duration, unique items, unique categories
    
    # Let's save the cleaned events first
    events_clean_path = os.path.join(PROC_DIR, 'events_cleaned.csv')
    df.to_csv(events_clean_path, index=False)
    
    # Grouping
    agg = df.groupby('session_uid').agg(
        visitorid=('visitorid', 'first'),
        start_time=('datetime', 'min'),
        end_time=('datetime', 'max'),
        view_count=('event', lambda x: (x == 'view').sum()),
        cart_count=('event', lambda x: (x == 'addtocart').sum()),
        purchase_count=('event', lambda x: (x == 'transaction').sum()),
        unique_items=('itemid', 'nunique'),
        unique_categories=('categoryid', 'nunique'),
        events_count=('event', 'count')
    ).reset_index()
    
    agg['elapsed_duration'] = (agg['end_time'] - agg['start_time']).dt.total_seconds()
    agg['has_purchase'] = (agg['purchase_count'] > 0).astype(int)
    
    # Save sessions
    sessions_path = os.path.join(PROC_DIR, 'sessions.csv')
    agg.to_csv(sessions_path, index=False)
    
    print("Creating SQLite DB...")
    db_path = os.path.join(PROC_DIR, 'db.sqlite')
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    df.to_sql('events', conn, index=False)
    agg.to_sql('sessions', conn, index=False)
    conn.close()
    
    print("Data processing complete.")

if __name__ == '__main__':
    os.makedirs(PROC_DIR, exist_ok=True)
    process_events()
