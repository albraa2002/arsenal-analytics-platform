"""
Match outcome prediction using XGBoost, Random Forest, and Logistic Regression.
Predicts: home_win / draw / away_win.
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

from config.config import config
from config.logging_config import get_logger


class MatchPredictor:
    """Predicts match outcomes using ensemble of models."""

    MODELS = {
        "xgboost": xgb.XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            objective="multi:softprob", num_class=3,
            random_state=42, eval_metric="mlogloss",
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200, max_depth=10,
            min_samples_split=5, random_state=42,
        ),
        "logistic_regression": LogisticRegression(
            multi_class="multinomial", max_iter=1000, C=1.0,
            random_state=42,
        ),
    }

    RESULTS_MAP = {"H": 0, "D": 1, "A": 2}

    def __init__(self, logger_name: str = "match_predictor"):
        self.logger = get_logger(logger_name)
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []

    def build_features(self, match_data: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        df = match_data.copy()
        features = []

        # Home team features
        for prefix in ["home_", "away_"]:
            features.extend([
                f"{prefix}xG", f"{prefix}xGA", f"{prefix}possession_pct",
                f"{prefix}shots", f"{prefix}shots_on_target",
                f"{prefix}ppda", f"{prefix}deep_completions",
                f"{prefix}corners", f"{prefix}fouls",
            ])

        # Derived features
        if "home_xG" in df.columns and "away_xG" in df.columns:
            df["xG_diff"] = df["home_xG"] - df["away_xG"]
            features.append("xG_diff")
        if "home_xGA" in df.columns and "away_xGA" in df.columns:
            df["xGA_diff"] = df["home_xGA"] - df["away_xGA"]
            features.append("xGA_diff")

        # Existing features
        existing = [f for f in features if f in df.columns]
        self.feature_names = existing

        X = df[existing].fillna(0)
        y = None
        if "result" in df.columns:
            y = df["result"].map(self.RESULTS_MAP).values

        return X, y

    def train(self, match_data: pd.DataFrame) -> Dict[str, float]:
        X, y = self.build_features(match_data)
        if y is None:
            self.logger.error("No target column 'result' found")
            return {}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        results = {}
        for name, model in self.MODELS.items():
            try:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                acc = accuracy_score(y_test, y_pred)
                self.models[name] = model
                results[name] = acc

                self.logger.info(
                    f"{name}: accuracy={acc:.3f}\n"
                    f"{classification_report(y_test, y_pred, target_names=['H', 'D', 'A'])}"
                )
            except Exception as exc:
                self.logger.error(f"{name} training failed: {exc}")

        return results

    def predict(self, match_features: pd.DataFrame) -> pd.DataFrame:
        features = match_features[self.feature_names].fillna(0)
        features_scaled = self.scaler.transform(features)

        predictions = {}
        probabilities = {}
        for name, model in self.models.items():
            preds = model.predict(features_scaled)
            probas = model.predict_proba(features_scaled)
            predictions[name] = [["H", "D", "A"][p] for p in preds]
            probabilities[name] = probas

        result_df = match_features.copy()
        for name in self.models:
            result_df[f"pred_{name}"] = predictions[name]
            for i, label in enumerate(["H", "D", "A"]):
                result_df[f"prob_{name}_{label}"] = probabilities[name][:, i]

        return result_df

    def save_models(self, path: str = ""):
        save_path = path or str(config.paths.models)
        import os
        os.makedirs(save_path, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"{save_path}/match_{name}.joblib")
        joblib.dump(self.scaler, f"{save_path}/match_scaler.joblib")
        self.logger.info(f"Models saved to {save_path}")

    def load_models(self, path: str = ""):
        load_path = path or str(config.paths.models)
        for name in self.MODELS:
            try:
                self.models[name] = joblib.load(f"{load_path}/match_{name}.joblib")
            except FileNotFoundError:
                self.logger.warning(f"Model {name} not found at {load_path}")
        try:
            self.scaler = joblib.load(f"{load_path}/match_scaler.joblib")
        except FileNotFoundError:
            pass
