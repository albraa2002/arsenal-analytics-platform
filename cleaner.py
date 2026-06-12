"""
Phase 2 — Data Cleaning

Handles:
- Missing value imputation (football-specific)
- Type conversion
- Duplicate removal
- Outlier detection (IQR, z-score)
- Football-specific cleaning (90s, per-90 rates, invalid pitch coords)
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from config.logging_config import get_logger


class DataCleaner:
    """Production-grade cleaning with football domain knowledge."""

    PITCH_X_RANGE: Tuple[float, float] = (0.0, 120.0)
    PITCH_Y_RANGE: Tuple[float, float] = (0.0, 80.0)

    # Columns that should never be negative in football context
    NON_NEGATIVE_COLS: List[str] = [
        "minutes", "goals", "assists", "shots", "shots_on_target",
        "passes", "touches", "tackles", "interceptions", "blocks",
        "clearances", "dribbles", "fouls", "yellow_cards", "red_cards",
        "saves", "goals_conceded", "clean_sheets", "starts",
        "games", "games_starts", "xG", "xA", "xGA",
    ]

    # Max reasonable values for per-game detection
    MAX_REASONABLE: Dict[str, float] = {
        "goals": 15, "assists": 10, "shots": 20, "shots_on_target": 12,
        "passes": 200, "touches": 250, "tackles": 20, "interceptions": 15,
        "clearances": 30, "dribbles": 25, "fouls": 10, "saves": 20,
        "goals_conceded": 15, "yellow_cards": 4, "red_cards": 2,
        "xG": 5.0, "xA": 3.0, "xGA": 5.0,
    }

    def __init__(self, logger_name: str = "cleaner"):
        self.logger = get_logger(logger_name)

    def clean(self, df: pd.DataFrame, source: str = "unknown") -> pd.DataFrame:
        df = df.copy()
        initial_rows = len(df)

        df = self._remove_duplicates(df, source)
        df = self._normalize_types(df, source)
        df = self._handle_missing(df, source)
        df = self._clamp_pitch_coordinates(df)
        df = self._enforce_non_negative(df)
        df = self._remove_outliers_iqr(df, source)

        self.logger.info(f"{source}: cleaned {initial_rows} → {len(df)} rows ({initial_rows - len(df)} removed)")
        return df

    def _remove_duplicates(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        if removed:
            self.logger.info(f"{source}: removed {removed} duplicates")
        return df

    def _normalize_types(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        for col in df.columns:
            if col in self.NON_NEGATIVE_COLS or any(k in col.lower() for k in ["x", "y", "id", "count", "pct", "ratio", "per_"]):
                df[col] = pd.to_numeric(df[col], errors="coerce")
            elif "date" in col.lower() or "time" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception:
                    pass
        return df

    def _handle_missing(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        threshold = 0.7
        missing_ratio = df.isnull().mean()
        high_missing = missing_ratio[missing_ratio > threshold].index.tolist()
        if high_missing:
            self.logger.info(f"{source}: dropping {len(high_missing)} cols with >{threshold:.0%} missing: {high_missing}")
            df = df.drop(columns=high_missing)

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                if col in self.NON_NEGATIVE_COLS:
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(df[col].median())

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].fillna("unknown")

        return df

    def _clamp_pitch_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if col in ("location_x", "end_location_x", "carry_end_location_x", "x"):
                df[col] = df[col].clip(*self.PITCH_X_RANGE)
            if col in ("location_y", "end_location_y", "carry_end_location_y", "y"):
                df[col] = df[col].clip(*self.PITCH_Y_RANGE)
        return df

    def _enforce_non_negative(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if any(nn in col.lower() for nn in ["count", "goals", "minutes", "x", "shots", "passes", "touches", "tackles", "saves", "fouls", "cards", "blocks", "clearances", "interceptions", "dribbles", "starts"]):
                if col in df.select_dtypes(include=[np.number]).columns:
                    neg_count = (df[col] < 0).sum()
                    if neg_count > 0:
                        self.logger.debug(f"Clamped {neg_count} negative values in {col}")
                        df[col] = df[col].clip(lower=0)
        return df

    def _remove_outliers_iqr(self, df: pd.DataFrame, source: str, factor: float = 4.0) -> pd.DataFrame:
        numeric = df.select_dtypes(include=[np.number]).columns
        before = len(df)
        outlier_mask = pd.Series(False, index=df.index)

        for col in numeric:
            if col in self.MAX_REASONABLE:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower = max(q1 - factor * iqr, 0)
                upper = q3 + factor * iqr
                col_outliers = (df[col] < lower) | (df[col] > upper)
                n_out = col_outliers.sum()
                if n_out > 0 and n_out < len(df) * 0.05:
                    outlier_mask = outlier_mask | col_outliers
                    self.logger.debug(f"{source}: flagged {n_out} outliers in {col}")

        df = df[~outlier_mask].copy()
        removed = before - len(df)
        if removed:
            self.logger.info(f"{source}: removed {removed} outlier rows")
        return df
