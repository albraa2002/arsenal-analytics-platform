"""
Player performance prediction using XGBoost regression.
Predicts: xG, xA, total_points, or any per-game metric.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

from config.config import config
from config.logging_config import get_logger


class PlayerPerformancePredictor:
    """Predicts player performance metrics using ensemble of regressors."""

    MODELS = {
        "xgboost": xgb.XGBRegressor(
            n_estimators=200, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=42,
        ),
        "random_forest": RandomForestRegressor(
            n_estimators=200, max_depth=8,
            min_samples_split=5, random_state=42,
        ),
    }

    DEFAULT_TARGET = "total_points"

    def __init__(self, target: str = "", logger_name: str = "player_performance"):
        self.target = target or self.DEFAULT_TARGET
        self.logger = get_logger(logger_name)
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []

    def build_features(self, player_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        df = player_data.copy()
        exclude = {self.target, "player_name", "resolved_name", "player_id",
                   "fpl_id", "season", "source", "match_id", "date_id"}
        feature_candidates = [c for c in df.columns if c not in exclude and df[c].dtype in (np.int64, np.float64)]

        # Add rolling averages if sufficient history
        df = df.sort_values("gameweek") if "gameweek" in df.columns else df

        self.feature_names = feature_candidates
        X = df[feature_candidates].fillna(0)

        y = None
        if self.target in df.columns:
            y = df[self.target].values

        return X, y

    def train(self, player_data: pd.DataFrame) -> Dict[str, float]:
        X, y = self.build_features(player_data)
        if y is None:
            self.logger.error(f"Target '{self.target}' not found")
            return {}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        results = {}
        for name, model in self.MODELS.items():
            try:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                self.models[name] = model
                results[name] = {"mae": mae, "rmse": rmse, "r2": r2}
                self.logger.info(f"{name} [{self.target}]: MAE={mae:.3f}, RMSE={rmse:.3f}, R²={r2:.3f}")
            except Exception as exc:
                self.logger.error(f"{name} failed: {exc}")

        return results

    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        f = features[self.feature_names].fillna(0)
        f_scaled = self.scaler.transform(f)
        result = features.copy()
        for name, model in self.models.items():
            result[f"pred_{self.target}_{name}"] = model.predict(f_scaled)
        return result

    def save_models(self, path: str = ""):
        save_path = path or str(config.paths.models)
        import os
        os.makedirs(save_path, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"{save_path}/perf_{self.target}_{name}.joblib")
        joblib.dump(self.scaler, f"{save_path}/perf_{self.target}_scaler.joblib")

    def load_models(self, path: str = ""):
        load_path = path or str(config.paths.models)
        for name in self.MODELS:
            try:
                self.models[name] = joblib.load(f"{load_path}/perf_{self.target}_{name}.joblib")
            except FileNotFoundError:
                self.logger.warning(f"Model {name} not found")
        try:
            self.scaler = joblib.load(f"{load_path}/perf_{self.target}_scaler.joblib")
        except FileNotFoundError:
            pass
