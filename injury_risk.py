"""
Injury risk estimation model.
Predicts injury probability based on player workload, minutes played,
match congestion, previous injuries, and physical metrics.
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, auc, precision_recall_curve, precision_score,
    recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

from config.config import config
from config.logging_config import get_logger


class InjuryRiskEstimator:
    """Binary classifier estimating injury risk (1 = high risk)."""

    MODELS = {
        "xgboost": xgb.XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.1,
            scale_pos_weight=3,  # Handle class imbalance
            random_state=42, eval_metric="aucpr",
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.1,
            random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=6,
            class_weight="balanced", random_state=42,
        ),
    }

    FEATURE_COLS = [
        "minutes_last_5", "minutes_last_3", "minutes_avg_90",
        "games_in_last_14_days", "days_since_last_match",
        "weekly_load_minutes", "fatigue_index",
        "age", "previous_injuries_season",
        "high_intensity_runs", "sprint_distance",
    ]

    def __init__(self, logger_name: str = "injury_risk"):
        self.logger = get_logger(logger_name)
        self.models = {}
        self.scaler = StandardScaler()

    def build_features(
        self, player_workload: pd.DataFrame, injury_labels: pd.Series = None
    ) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        df = player_workload.copy()
        existing = [c for c in self.FEATURE_COLS if c in df.columns]
        X = df[existing].fillna(0)

        y = None
        if injury_labels is not None:
            y = injury_labels.values

        return X, y

    def train(self, workload: pd.DataFrame, labels: pd.Series) -> Dict[str, float]:
        X, y = self.build_features(workload, labels)
        if y is None:
            self.logger.error("No injury labels provided")
            return {}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        results = {}
        for name, model in self.MODELS.items():
            try:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_proba = model.predict_proba(X_test_scaled)[:, 1]

                acc = accuracy_score(y_test, y_pred)
                prec = precision_score(y_test, y_pred, zero_division=0)
                rec = recall_score(y_test, y_pred, zero_division=0)
                roc_auc = roc_auc_score(y_test, y_proba)

                self.models[name] = model
                results[name] = {"accuracy": acc, "precision": prec, "recall": rec, "roc_auc": roc_auc}
                self.logger.info(f"{name}: acc={acc:.3f}, prec={prec:.3f}, rec={rec:.3f}, AUC={roc_auc:.3f}")
            except Exception as exc:
                self.logger.error(f"{name} failed: {exc}")

        return results

    def predict_risk(self, workload: pd.DataFrame) -> pd.DataFrame:
        X = workload[[c for c in self.FEATURE_COLS if c in workload.columns]].fillna(0)
        X_scaled = self.scaler.transform(X)
        result = workload.copy()

        for name, model in self.models.items():
            result[f"injury_risk_{name}"] = model.predict_proba(X_scaled)[:, 1]

        if self.models:
            risk_cols = [c for c in result.columns if "injury_risk_" in c]
            result["injury_risk_ensemble"] = result[risk_cols].mean(axis=1)
            result["injury_risk_level"] = pd.cut(
                result["injury_risk_ensemble"],
                bins=[0, 0.3, 0.6, 1.0],
                labels=["Low", "Medium", "High"],
            )

        return result

    def save_models(self, path: str = ""):
        save_path = path or str(config.paths.models)
        import os
        os.makedirs(save_path, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"{save_path}/injury_{name}.joblib")
        joblib.dump(self.scaler, f"{save_path}/injury_scaler.joblib")

    def load_models(self, path: str = ""):
        load_path = path or str(config.paths.models)
        for name in self.MODELS:
            try:
                self.models[name] = joblib.load(f"{load_path}/injury_{name}.joblib")
            except FileNotFoundError:
                self.logger.warning(f"Model {name} not found")
        try:
            self.scaler = joblib.load(f"{load_path}/injury_scaler.joblib")
        except FileNotFoundError:
            pass
