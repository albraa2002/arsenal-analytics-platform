"""
Team-level advanced metrics including PPDA, possession %, field tilt,
build-up speed, final third entries, progressive distance, and counter-pressing.
"""

import numpy as np
import pandas as pd

from config.logging_config import get_logger


class TeamMetricsEngine:
    """Computes advanced team-level football metrics."""

    def __init__(self, logger_name: str = "team_metrics"):
        self.logger = get_logger(logger_name)

    def compute_all(self, events_df: pd.DataFrame, team_id: int = None) -> pd.DataFrame:
        metrics = {}

        metrics["ppda"] = self.compute_ppda(events_df, team_id)
        metrics["possession_pct"] = self.compute_possession_pct(events_df, team_id)
        metrics["field_tilt"] = self.compute_field_tilt(events_df, team_id)
        metrics["final_third_entries"] = self.compute_final_third_entries(events_df, team_id)
        metrics["progressive_distance"] = self.compute_progressive_distance(events_df, team_id)
        metrics["counter_pressures"] = self.compute_counter_pressing(events_df, team_id)
        metrics["build_up_speed"] = self.compute_build_up_speed(events_df, team_id)

        return pd.DataFrame([metrics])

    def compute_ppda(
        self, events: pd.DataFrame, team_id: int = None
    ) -> float:
        """Passes Per Defensive Action — passes allowed / defensive actions in final 60%."""
        defensive_actions = events[
            (events["event_type"].isin(["Tackle", "Interception", "Foul", "Clearance", "Block"]))
            & (events["location_x"] < 80)
        ]
        n_actions = len(defensive_actions)

        own_passes = events[
            (events["event_type"] == "Pass")
            & (events["team_id"] != team_id)
        ]
        n_passes = len(own_passes)

        if n_actions == 0:
            return 999.0
        return round(n_passes / n_actions, 2)

    def compute_possession_pct(
        self, events: pd.DataFrame, team_id: int = None
    ) -> float:
        """Estimate possession from pass and carry events."""
        team_events = events[events["team_id"] == team_id]
        opp_events = events[events["team_id"] != team_id]

        team_touches = len(team_events[team_events["event_type"].isin(["Pass", "Carry", "Ball Receipt*", "Dribble"])])
        opp_touches = len(opp_events[opp_events["event_type"].isin(["Pass", "Carry", "Ball Receipt*", "Dribble"])])

        total = team_touches + opp_touches
        if total == 0:
            return 50.0
        return round(team_touches / total * 100, 1)

    def compute_field_tilt(self, events: pd.DataFrame, team_id: int = None) -> float:
        """Ratio of passes in attacking third vs defensive third."""
        att_third = 80
        own_passes_att = events[
            (events["event_type"] == "Pass")
            & (events["team_id"] == team_id)
            & (events["location_x"] >= att_third)
        ]
        opp_passes_att = events[
            (events["event_type"] == "Pass")
            & (events["team_id"] != team_id)
            & (events["location_x"] >= att_third)
        ]
        own_count = len(own_passes_att)
        opp_count = len(opp_passes_att)
        total = own_count + opp_count
        if total == 0:
            return 50.0
        return round(own_count / total * 100, 1)

    def compute_final_third_entries(self, events: pd.DataFrame, team_id: int = None) -> int:
        """Count of carries and passes that enter the final third."""
        entries = events[
            (events["team_id"] == team_id)
            & (
                (events["end_location_x"] >= 80)
                & (events["location_x"] < 80)
            )
            & (events["event_type"].isin(["Pass", "Carry"]))
        ]
        return len(entries)

    def compute_progressive_distance(self, events: pd.DataFrame, team_id: int = None) -> float:
        """Total progressive pass/carry distance."""
        progressive = events[
            (events["team_id"] == team_id)
            & (events["event_type"].isin(["Pass", "Carry"]))
            & (events["end_location_x"].notna())
            & (events["location_x"].notna())
        ]
        distances = progressive["end_location_x"] - progressive["location_x"]
        progressive_dist = distances[distances > 0].sum()
        return round(progressive_dist, 1)

    def compute_counter_pressing(self, events: pd.DataFrame, team_id: int = None) -> int:
        """Number of counter-press events (within 5s of losing possession)."""
        counterpress = events[
            (events["counterpress"] == True)  # noqa: E712
            & (events["team_id"] == team_id)
        ]
        return len(counterpress)

    def compute_build_up_speed(self, events: pd.DataFrame, team_id: int = None) -> float:
        """Average seconds per possession sequence."""
        team_events = events[events["team_id"] == team_id].sort_values(["match_id", "minute", "second"])
        if team_events.empty:
            return 0.0
        avg_speed = team_events.groupby("possession").apply(
            lambda g: g["second"].max() - g["second"].min()
            if len(g) > 1 and g["second"].notna().any()
            else 0
        ).mean()
        return round(float(avg_speed), 2)
