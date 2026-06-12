"""
Column normalizer — standardizes column names across all sources into
a consistent snake_case schema with football-specific terminology.
"""

import re
from typing import Dict

import pandas as pd

from config.logging_config import get_logger


class ColumnNormalizer:
    """Maps raw column names from each source to a standardised schema."""

    # Source-specific column mappings
    FBREF_MAP: Dict[str, str] = {
        "player": "player_name",
        "nation": "nationality",
        "pos": "position",
        "squad": "team_name",
        "age": "age",
        "born": "birth_year",
        "mp": "matches_played",
        "starts": "starts",
        "min": "minutes",
        "gls": "goals",
        "ast": "assists",
        "pk": "penalty_kicks_made",
        "pkat": "penalty_kicks_attempted",
        "crdy": "yellow_cards",
        "crdr": "red_cards",
        "xg": "xG",
        "npxg": "npxG",
        "xag": "xA",
        "g-xg": "goals_minus_xG",
        "np:g-xg": "np_goals_minus_xG",
        "sh": "shots_total",
        "sot": "shots_on_target",
        "soT_": "shots_on_target",
        "sh/90": "shots_per_90",
        "sot/90": "shots_on_target_per_90",
        "g/sh": "goals_per_shot",
        "g/sot": "goals_per_shot_on_target",
        "dist": "shot_distance",
        "fk": "free_kick_goals",
        "pkatt": "penalty_attempted",
        "pkw": "penalty_won",
        "g-pk": "non_penalty_goals",
        "passes_completed": "passes",
        "passes_attempted": "passes_attempted",
        "passes_completed_short": "short_passes",
        "passes_attempted_short": "short_passes_attempted",
        "passes_completed_medium": "medium_passes",
        "passes_attempted_medium": "medium_passes_attempted",
        "passes_completed_long": "long_passes",
        "passes_attempted_long": "long_passes_attempted",
        "pass_total_distance": "pass_distance_total",
        "pass_progressive_distance": "pass_distance_progressive",
        "progressive_passes": "progressive_passes",
        "passes_into_final_third": "passes_into_final_third",
        "passes_into_penalty_area": "passes_into_penalty_area",
        "crosses_into_penalty_area": "crosses_into_penalty_area",
        "progressive_carries": "progressive_carries",
        "carries_total_distance": "carry_distance_total",
        "carries_progressive_distance": "carry_distance_progressive",
        "carries_into_final_third": "carries_into_final_third",
        "carries_into_penalty_area": "carries_into_penalty_area",
        "touches": "touches",
        "touches_def_pen_area": "touches_defensive_penalty_area",
        "touches_def_3rd": "touches_defensive_third",
        "touches_mid_3rd": "touches_mid_third",
        "touches_att_3rd": "touches_attacking_third",
        "touches_att_pen_area": "touches_attacking_penalty_area",
        "passes_received": "passes_received",
        "sca": "shot_creating_actions",
        "gca": "goal_creating_actions",
        "tkl": "tackles",
        "tklw": "tackles_won",
        "def_3rd_tkl": "tackles_defensive_third",
        "mid_3rd_tkl": "tackles_mid_third",
        "att_3rd_tkl": "tackles_attacking_third",
        "int": "interceptions",
        "clr": "clearances",
        "err": "errors_leading_to_shot",
        "blocks": "blocks",
        "sh_blocked": "shots_blocked",
        "pass_blocked": "passes_blocked",
        "ga": "goals_against",
        "ga90": "goals_against_per_90",
        "soT_against": "shots_on_target_against",
        "saves": "saves",
        "save_pct": "save_percentage",
        "cs": "clean_sheets",
        "pkatt_against": "penalties_faced",
        "pksv": "penalties_saved",
        "sv_pct": "penalty_save_percentage",
        "pk_against": "penalties_conceded",
        "pksv_pct": "penalty_save_percentage",
        "pkm_against": "penalties_missed_against",
    }

    UNDERSTAT_MAP: Dict[str, str] = {
        "player_name": "player_name",
        "team_title": "team_name",
        "games": "matches_played",
        "time": "minutes",
        "goals": "goals",
        "xG": "xG",
        "xGAssists": "xA",
        "shots": "shots_total",
        "key_passes": "key_passes",
        "xGShot": "xG_per_shot",
        "assists": "assists",
        "season": "season",
    }

    FPL_MAP: Dict[str, str] = {
        "first_name": "first_name",
        "second_name": "last_name",
        "web_name": "short_name",
        "now_cost": "current_price",
        "selected_by_percent": "ownership_pct",
        "points_per_game": "ppg",
        "total_points": "total_points",
        "element_type": "position_id",
        "team_fpl_id": "fpl_team_id",
        "expected_goals": "xG",
        "expected_assists": "xA",
        "expected_goal_involvements": "xGI",
        "expected_goals_conceded": "xGC",
        "ict_index": "ict_index",
    }

    def __init__(self):
        self.logger = get_logger("normalizer")

    def normalize(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        mapping = self._get_mapping(source)
        df = df.rename(columns=mapping)
        df = self._standardize_names(df)
        df = self._add_source_tag(df, source)
        return df

    def _get_mapping(self, source: str) -> Dict[str, str]:
        if "fbref" in source.lower():
            return {k: v for k, v in self.FBREF_MAP.items()}
        if "understat" in source.lower():
            return {k: v for k, v in self.UNDERSTAT_MAP.items()}
        if "fpl" in source.lower():
            return {k: v for k, v in self.FPL_MAP.items()}
        return {}

    def _standardize_names(self, df: pd.DataFrame) -> pd.DataFrame:
        rename = {}
        for col in df.columns:
            new = col.lower().strip()
            new = re.sub(r"[^a-z0-9_]", "_", new)
            new = re.sub(r"_+", "_", new).strip("_")
            if new != col.lower():
                rename[col] = new
        return df.rename(columns=rename)

    def _add_source_tag(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        if "source" not in df.columns:
            df["source"] = source.lower()
        return df
