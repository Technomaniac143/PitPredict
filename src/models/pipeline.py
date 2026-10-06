import os
import random
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_absolute_error, r2_score, precision_score, recall_score, f1_score
from typing import List, Tuple, Dict, Any

from src.data.ingestion import fetch_session_data
from src.features.engineering import engineer_features

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'artifacts')
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

class PitPredictPipeline:
    def __init__(self):
        # GPU Acceleration disabled to prevent Streamlit CUDA threading deadlocks
        self.xgb_reg = XGBRegressor(
            n_estimators=150, learning_rate=0.1, max_depth=5, 
            random_state=42, tree_method='hist', device='cpu'
        )
        self.xgb_clf = XGBClassifier(
            n_estimators=150, eval_metric='logloss', 
            random_state=42, tree_method='hist', device='cpu'
        )
        
        self.data = pd.DataFrame()
        self.is_trained = False
        self.metrics = {}
        self.feature_importances = {}
        
    def train(self, races: List[Tuple[int, str]] = None, test_race: Tuple[int, str] = None):
        if races is None:
            races = [(2021, 'Spain')]
            
        all_dfs = []
        for year, gp in races:
            df = fetch_session_data(year, gp)
            if not df.empty:
                all_dfs.append(df)
                
        if not all_dfs:
            print("No training data loaded.")
            return False
            
        train_df_raw = pd.concat(all_dfs, ignore_index=True)
        train_df_featured = engineer_features(train_df_raw)
        self.data = train_df_featured
        
        if test_race is not None:
            test_df_raw = fetch_session_data(test_race[0], test_race[1])
            test_df = engineer_features(test_df_raw)
            train_df = train_df_featured
        else:
            drivers = train_df_featured['Driver'].dropna().unique()
            drivers = sorted(list(drivers))
            random.seed(42)
            test_drivers = random.sample(drivers, max(1, int(len(drivers) * 0.2)))
            print(f"Driver-based holdout. Test drivers: {test_drivers}")
            
            test_df = train_df_featured[train_df_featured['Driver'].isin(test_drivers)].copy()
            train_df = train_df_featured[~train_df_featured['Driver'].isin(test_drivers)].copy()
            
        self._train_regression(train_df, test_df)
        self._train_classification(train_df, test_df)
        
        self.is_trained = True
        self.save_models()
        return True

    def _train_regression(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        features = ['Tire_Age', 'Compound_Encoded', 'Track_State', 'Weather_Index', 'Pace_Volatility']
        
        def prep_data(df):
            clean = df[df['PitOutTime'].isna() & df['PitInTime'].isna()].copy()
            return clean.dropna(subset=features + ['LapTime_Seconds'])
            
        train_reg = prep_data(train_df)
        test_reg = prep_data(test_df)
        
        if not train_reg.empty:
            self.xgb_reg.fit(train_reg[features], train_reg['LapTime_Seconds'])
            
            if not test_reg.empty:
                preds = self.xgb_reg.predict(test_reg[features])
                self.metrics['regression'] = {
                    'MAE': float(mean_absolute_error(test_reg['LapTime_Seconds'], preds)),
                    'R2': float(r2_score(test_reg['LapTime_Seconds'], preds))
                }
            self.feature_importances['regression'] = dict(zip(features, [float(v) for v in self.xgb_reg.feature_importances_]))
            
    def _train_classification(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        features = ['Tire_Age', 'Compound_Encoded', 'Gap_to_Car_Ahead', 'In_Dirty_Air', 'Track_State', 'Pace_Volatility', 'Pit_Cost_Delta']
        
        def prep_data(df):
            return df.dropna(subset=features + ['Is_Pit_Lap'])
            
        train_clf = prep_data(train_df)
        test_clf = prep_data(test_df)
        
        if not train_clf.empty:
            self.xgb_clf.fit(train_clf[features], train_clf['Is_Pit_Lap'])
            
            if not test_clf.empty:
                preds = self.xgb_clf.predict(test_clf[features])
                y_true = test_clf['Is_Pit_Lap']
                y_naive = np.zeros_like(y_true)
                
                self.metrics['classification'] = {
                    'Precision': float(precision_score(y_true, preds, zero_division=0)),
                    'Recall': float(recall_score(y_true, preds, zero_division=0)),
                    'F1': float(f1_score(y_true, preds, zero_division=0)),
                    'Naive_F1': float(f1_score(y_true, y_naive, zero_division=0))
                }
            self.feature_importances['classification'] = dict(zip(features, [float(v) for v in self.xgb_clf.feature_importances_]))

    def predict_for_driver(self, driver_id: str) -> Dict[str, Any]:
        if not self.is_trained or self.data.empty:
            return None
            
        driver_data = self.data[self.data['Driver'] == driver_id].copy()
        if driver_data.empty:
            return None
            
        features_reg = ['Tire_Age', 'Compound_Encoded', 'Track_State', 'Weather_Index', 'Pace_Volatility']
        reg_input = driver_data.dropna(subset=features_reg)
        lap_preds = self.xgb_reg.predict(reg_input[features_reg]).tolist() if not reg_input.empty else []
        
        features_clf = ['Tire_Age', 'Compound_Encoded', 'Gap_to_Car_Ahead', 'In_Dirty_Air', 'Track_State', 'Pace_Volatility', 'Pit_Cost_Delta']
        clf_input = driver_data.dropna(subset=features_clf)
        pit_probs = self.xgb_clf.predict_proba(clf_input[features_clf])[:, 1].tolist() if not clf_input.empty else []
            
        return {
            "driver": driver_id,
            "laps": driver_data['LapNumber'].dropna().tolist(),
            "actual_lap_times": driver_data['LapTime_Seconds'].dropna().tolist(),
            "predicted_lap_times": lap_preds,
            "pit_probabilities": pit_probs,
            "tire_age": driver_data['Tire_Age'].dropna().tolist(),
            "is_pit_lap": driver_data['Is_Pit_Lap'].dropna().tolist()
        }

    def save_models(self):
        joblib.dump(self.xgb_reg, os.path.join(MODEL_DIR, 'xgb_reg.joblib'))
        joblib.dump(self.xgb_clf, os.path.join(MODEL_DIR, 'xgb_clf.joblib'))
        joblib.dump(self.metrics, os.path.join(MODEL_DIR, 'metrics.joblib'))
        joblib.dump(self.feature_importances, os.path.join(MODEL_DIR, 'importances.joblib'))

    def load_models(self) -> bool:
        try:
            self.xgb_reg = joblib.load(os.path.join(MODEL_DIR, 'xgb_reg.joblib'))
            self.xgb_clf = joblib.load(os.path.join(MODEL_DIR, 'xgb_clf.joblib'))
            
            # Force CPU for inference to prevent CUDA multithreading context crashes in Streamlit
            self.xgb_reg.set_params(device='cpu')
            self.xgb_clf.set_params(device='cpu')
            
            self.metrics = joblib.load(os.path.join(MODEL_DIR, 'metrics.joblib'))
            self.feature_importances = joblib.load(os.path.join(MODEL_DIR, 'importances.joblib'))
            self.is_trained = True
            return True
        except Exception:
            return False

pipeline_instance = PitPredictPipeline()
