import os
import fastf1
import pandas as pd

# Setup Cache Directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'f1_cache')
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
fastf1.Cache.enable_cache(CACHE_DIR)

def fetch_session_data(year: int, gp: str, session_type: str = 'R') -> pd.DataFrame:
    """
    Fetches F1 session data including laps and weather, merging them correctly.
    """
    try:
        print(f"Fetching {year} {gp} {session_type}...")
        session = fastf1.get_session(year, gp, session_type)
        session.load(laps=True, telemetry=False, weather=True, messages=False)

        if len(session.laps) == 0:
            print(f"No lap data found for {year} {gp}")
            return pd.DataFrame()

        laps = session.laps.copy()
        weather = session.weather_data.copy()

        # Convert Time to total seconds for merging
        laps['Time_Seconds'] = laps['Time'].dt.total_seconds()
        
        if not weather.empty:
            weather['Time_Seconds'] = weather['Time'].dt.total_seconds()
            # Merge weather into laps backwards to get the most recent weather reading per lap
            merged = pd.merge_asof(
                laps.sort_values('Time_Seconds'),
                weather.sort_values('Time_Seconds'),
                on='Time_Seconds',
                direction='backward'
            )
        else:
            merged = laps.copy()
            merged['AirTemp'] = 25.0
            merged['TrackTemp'] = 35.0
            merged['Rainfall'] = False

        merged['Year'] = year
        merged['GP'] = gp
        return merged
    
    except Exception as e:
        print(f"Critical error loading {year} {gp}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Test execution
    df = fetch_session_data(2021, 'Spain')
    print(df.head())
