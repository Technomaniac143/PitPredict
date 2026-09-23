import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw FastF1 telemetry and laps into ML-ready features.
    Now includes advanced F1 metrics: Traffic Density, Track State, and Pit Cost.
    """
    if df.empty:
        return df

    # Feature 1: Tire Age (Laps since last pit stop)
    df = df.sort_values(['Driver', 'LapNumber'])
    df['Tire_Age'] = df.groupby(['Driver', 'Stint'])['LapNumber'].cumcount() + 1
    
    # Feature 2: Lap Time & Delta
    df['LapTime_Seconds'] = df['LapTime'].dt.total_seconds()
    df['Lap_Delta'] = df.groupby('Driver')['LapTime_Seconds'].diff()
    
    # Feature 3: Driver Aggressiveness (Pace Volatility)
    # Calculated as the rolling standard deviation of Lap_Delta over the last 3 laps
    df['Pace_Volatility'] = df.groupby('Driver')['Lap_Delta'].transform(lambda x: x.rolling(window=3, min_periods=1).std()).fillna(0)
    
    # Feature 4: Weather Index
    df['Weather_Index'] = df['AirTemp'] + (df['Rainfall'].astype(int) * 10)
    
    # Feature 5: Track State (Macro Evolution)
    # Simulates rubber laying down. 
    df['Track_State'] = df['LapNumber'] * (df['TrackTemp'] / 30.0)

    # Feature 6: True Gap to Car Ahead & Traffic Density
    df = df.sort_values(['LapNumber', 'Time_Seconds'])
    df['Gap_to_Car_Ahead'] = df.groupby('LapNumber')['Time_Seconds'].diff().fillna(0)
    
    # Traffic Density: Flag if caught in "dirty air" (within 1.5s of car ahead)
    df['In_Dirty_Air'] = (df['Gap_to_Car_Ahead'] < 1.5).astype(int)

    # Feature 7: Pit Stop Cost Delta
    # A standard constant for strategic calculations (e.g. 22 seconds for Spain)
    df['Pit_Cost_Delta'] = 22.0

    # Feature 8: Compound Encoding
    compound_mapping = {'SOFT': 0, 'MEDIUM': 1, 'HARD': 2, 'INTERMEDIATE': 3, 'WET': 4}
    if 'Compound' in df.columns:
        df['Compound_Encoded'] = df['Compound'].map(compound_mapping).fillna(5)
    else:
        df['Compound_Encoded'] = 5

    # Clean missing values
    cols_to_fix = ['LapTime_Seconds', 'Lap_Delta', 'TrackTemp', 'AirTemp']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = df[col].ffill().bfill()
            
    # Target Variable: Is this a pit lap?
    df['Is_Pit_Lap'] = df['PitInTime'].notna().astype(int)

    df = df.sort_values(['Driver', 'LapNumber']).reset_index(drop=True)
    return df
