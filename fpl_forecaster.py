"""
FPL Intelligence — forecasts expected points, optimal transfers,
and player value using time-series and regression models.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

from config.config import config
from config.logging_config import get_logger


class FPLForecaster:
    """Forecasts FPL points, identifies value picks, and optimises transfers."""

    MODELS = {
        "xgboost": xgb.XGBRegressor(
            n_estimators=150, max_depth=4, learning_rate=0.05,
            random_state=42,
        ),
        "ridge": Ridge(alpha=1.0, random_state=42),
        "linear": LinearRegression(),
    }

    def __init__(self, logger_name: str = "fpl_forecaster"):
        self.logger = get_logger(logger_name)
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []

    def build_features(self, fpl_data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        df = fpl_data.copy()
        exclude = {"total_points", "player_name", "fpl_id", "season",
                   "gameweek", "team_name", "position"}
        features = [c for c in df.columns if c not in exclude and df[c].dtype in (np.int64, np.float64, bool)]

        # Add lag features
        if "gameweek" in df.columns:
            for lag in [1, 2, 3]:
                for col in ["total_points", "minutes", "xG", "xA"]:
                    if col in df.columns:
                        df[f"{col}_lag_{lag}"] = df.groupby("fpl_id")[col].shift(lag)
                        features.append(f"{col}_lag_{lag}")

        # Rolling averages
        if "gameweek" in df.columns:
            for window in [3, 5]:
                for col in ["total_points", "minutes", "xG"]:
                    if col in df.columns:
                        df[f"{col}_rolling_{window}"] = (
                            df.groupby("fpl_id")[col].transform(
                                lambda x: x.rolling(window, min_periods=1).mean()
                            )
                        )
                        features.append(f"{col}_rolling_{window}")

        self.feature_names = [f for f in features if f in df.columns]
        X = df[self.feature_names].fillna(0)

        y = None
        if "total_points" in df.columns:
            y = df["total_points"].values

        return X, y

    def train(self, fpl_data: pd.DataFrame) -> Dict[str, float]:
        X, y = self.build_features(fpl_data)
        if y is None:
            self.logger.error("No total_points target column")
            return {}

        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        results = {}
        for name, model in self.MODELS.items():
            try:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                self.models[name] = model
                results[name] = {"mae": mae}
                self.logger.info(f"FPL {name}: MAE={mae:.3f}")
            except Exception as exc:
                self.logger.error(f"FPL {name} failed: {exc}")

        return results

    def predict_next_gameweek(self, fpl_data: pd.DataFrame) -> pd.DataFrame:
        X, _ = self.build_features(fpl_data)
        X_scaled = self.scaler.transform(X)

        result = fpl_data[["fpl_id", "player_name", "web_name", "now_cost", "position"]].copy()
        for name, model in self.models.items():
            result[f"predicted_points_{name}"] = model.predict(X_scaled)

        if self.models:
            pred_cols = [c for c in result.columns if "predicted_points_" in c]
            result["predicted_points"] = result[pred_cols].mean(axis=1)
            result["value_score"] = np.where(
                result["now_cost"] > 0,
                (result["predicted_points"] / result["now_cost"] * 10).round(2),
                0,
            )

        return result.sort_values("predicted_points", ascending=False)

    def identify_transfer_targets(
        self, current_squad: pd.DataFrame, all_players: pd.DataFrame
    ) -> pd.DataFrame:
        """Recommend transfers: replace underperformers with value picks."""
        predictions = self.predict_next_gameweek(all_players)

        # Players not in current squad, sorted by value
        available = predictions[~predictions["fpl_id"].isin(current_squad["fpl_id"])]
        available = available.sort_values("value_score", ascending=False)

        # Current squad underperformers
        current = predictions[predictions["fpl_id"].isin(current_squad["fpl_id"])]
        underperformers = current[current["predicted_points"] < current["predicted_points"].median()]
        underperformers = underperformers.sort_values("predicted_points")

        return pd.DataFrame({
            "out_player": underperformers["player_name"].values[:5],
            "out_predicted_pts": underperformers["predicted_points"].values[:5],
            "in_player": available["player_name"].values[:5],
            "in_predicted_pts": available["predicted_points"].values[:5],
            "value_gain": (
                available["predicted_points"].values[:5]
                - underperformers["predicted_points"].values[:5]
            ),
        })

    def save_models(self, path: str = ""):
        save_path = path or str(config.paths.models)
        import os
        os.makedirs(save_path, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"{save_path}/fpl_{name}.joblib")
        joblib.dump(self.scaler, f"{save_path}/fpl_scaler.joblib")

    def load_models(self, path: str = ""):
        load_path = path or str(config.paths.models)
        for name in self.MODELS:
            try:
                self.models[name] = joblib.load(f"{load_path}/fpl_{name}.joblib")
            except FileNotFoundError:
                self.logger.warning(f"Model {name} not found")
        try:
            self.scaler = joblib.load(f"{load_path}/fpl_scaler.joblib")
        except FileNotFoundError:
            pass
