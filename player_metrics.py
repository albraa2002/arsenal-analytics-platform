"""
Player-level advanced metrics: xG/90, xA/90, progressive passes/carries/90,
pressures, ball recoveries, passing into final third, and more.
"""

import numpy as np
import pandas as pd

from config.logging_config import get_logger


class PlayerMetricsEngine:
    """Computes per-90 and advanced player metrics."""

    def __init__(self, logger_name: str = "player_metrics"):
        self.logger = get_logger(logger_name)

    def compute_all(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        df = stats_df.copy()
        df = self.compute_per_90(df)
        df = self.compute_efficiency_rates(df)
        df = self.compute_creative_metrics(df)
        df = self.compute_defensive_metrics(df)
        self.logger.info(f"Computed player metrics for {len(df)} rows")
        return df

    def compute_per_90(self, df: pd.DataFrame) -> pd.DataFrame:
        minute_cols = ["minutes", "min", "time", "minutes_played"]
        minutes_col = next((c for c in minute_cols if c in df.columns), None)
        if minutes_col is None:
            return df

        per_90_pairs = [
            ("goals", "goals_per_90"),
            ("assists", "assists_per_90"),
            ("xG", "xG_per_90"),
            ("xA", "xA_per_90"),
            ("shots_total", "shots_per_90"),
            ("shots_on_target", "sot_per_90"),
            ("progressive_passes", "progressive_passes_per_90"),
            ("progressive_carries", "progressive_carries_per_90"),
            ("touches", "touches_per_90"),
            ("passes", "passes_per_90"),
            ("key_passes", "key_passes_per_90"),
            ("tackles", "tackles_per_90"),
            ("interceptions", "interceptions_per_90"),
            ("blocks", "blocks_per_90"),
            ("clearances", "clearances_per_90"),
            ("dribbles_completed", "dribbles_completed_per_90"),
            ("fouls", "fouls_per_90"),
            ("fouls_drawn", "fouls_drawn_per_90"),
            ("passes_into_final_third", "passes_into_final_third_per_90"),
            ("passes_into_penalty_area", "passes_into_pen_area_per_90"),
        ]

        for raw_col, new_col in per_90_pairs:
            if raw_col in df.columns:
                df[new_col] = (df[raw_col] / df[minutes_col].clip(lower=1)) * 90
                df[new_col] = df[new_col].fillna(0).round(2)

        return df

    def compute_efficiency_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        if "goals" in df.columns and "shots_total" in df.columns:
            df["shot_conversion_pct"] = (
                np.where(df["shots_total"] > 0, df["goals"] / df["shots_total"] * 100, 0)
            ).round(1)

        if "shots_on_target" in df.columns and "shots_total" in df.columns:
            df["shot_accuracy_pct"] = (
                np.where(df["shots_total"] > 0, df["shots_on_target"] / df["shots_total"] * 100, 0)
            ).round(1)

        if "passes" in df.columns and "passes_accurate" in df.columns:
            df["pass_completion_pct"] = (
                np.where(df["passes"] > 0, df["passes_accurate"] / df["passes"] * 100, 0)
            ).round(1)

        if "dribbles_completed" in df.columns and "dribbles_attempted" in df.columns:
            df["dribble_success_pct"] = (
                np.where(df["dribbles_attempted"] > 0, df["dribbles_completed"] / df["dribbles_attempted"] * 100, 0)
            ).round(1)

        if "aerial_duels_won" in df.columns and "aerial_duels_lost" in df.columns:
            total_aerial = df["aerial_duels_won"] + df["aerial_duels_lost"]
            df["aerial_win_pct"] = (
                np.where(total_aerial > 0, df["aerial_duels_won"] / total_aerial * 100, 0)
            ).round(1)

        return df

    def compute_creative_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        if "xG" in df.columns and "goals" in df.columns:
            df["g_minus_xG"] = (df["goals"] - df["xG"]).round(2)
            df["xG_overperformance"] = np.where(
                df["xG"] > 0, (df["goals"] / df["xG"]).round(2), 0
            )

        if "xA" in df.columns and "assists" in df.columns:
            df["a_minus_xA"] = (df["assists"] - df["xA"]).round(2)

        if "shots_total" in df.columns and "key_passes" in df.columns:
            df["shot_creating_actions_per_90"] = (
                (df["shots_total"] + df["key_passes"]) / df["minutes"].clip(lower=1) * 90
            ).round(2)

        return df

    def compute_defensive_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        if "tackles" in df.columns:
            df["defensive_actions"] = df[
                [c for c in ["tackles", "interceptions", "blocks", "clearances"]
                 if c in df.columns]
            ].sum(axis=1)

        if "defensive_actions" in df.columns and "minutes" in df.columns:
            df["defensive_actions_per_90"] = (
                df["defensive_actions"] / df["minutes"].clip(lower=1) * 90
            ).round(2)

        if "touches_defensive_third" in df.columns and "touches" in df.columns:
            df["defensive_touch_pct"] = (
                np.where(df["touches"] > 0, df["touches_defensive_third"] / df["touches"] * 100, 0)
            ).round(1)

        return df
