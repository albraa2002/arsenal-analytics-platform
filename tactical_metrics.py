"""
Tactical metrics: average positions, passing networks, zone 14 entries,
shot zones, and defensive line height.
"""

import numpy as np
import pandas as pd

from config.logging_config import get_logger


class TacticalMetricsEngine:
    """Computes tactical / systems-level metrics from event data."""

    ZONE14_X_MIN: float = 78.0
    ZONE14_X_MAX: float = 90.0
    ZONE14_Y_MIN: float = 30.0
    ZONE14_Y_MAX: float = 50.0

    SHOT_ZONES: dict = {
        "six_yard_box": {"x": (102, 110), "y": (30, 38)},
        "penalty_area": {"x": (90, 110), "y": (18, 50)},
        "edge_of_box": {"x": (78, 90), "y": (18, 50)},
        "long_range": {"x": (0, 78), "y": (0, 68)},
    }

    def __init__(self, logger_name: str = "tactical_metrics"):
        self.logger = get_logger(logger_name)

    def compute_average_positions(
        self, events: pd.DataFrame, formation: str = None
    ) -> pd.DataFrame:
        """Compute average player positions from event locations."""
        position_events = events[
            events["event_type"].isin(["Pass", "Carry", "Ball Receipt*", "Dribble"])
        ]

        avg_pos = (
            position_events.groupby("player_name")
            .agg(
                avg_x=("location_x", "mean"),
                avg_y=("location_y", "mean"),
                touch_count=("event_id", "count"),
            )
            .reset_index()
        )
        avg_pos["avg_x"] = avg_pos["avg_x"].round(1)
        avg_pos["avg_y"] = avg_pos["avg_y"].round(1)
        return avg_pos

    def compute_passing_network(self, events: pd.DataFrame) -> pd.DataFrame:
        """Count pass connections between each pair of players."""
        passes = events[
            (events["event_type"] == "Pass")
            & (events["player_name"].notna())
            & (events["pass_recipient"].notna())
        ]

        network = (
            passes.groupby(["player_name", "pass_recipient"])
            .agg(
                pass_count=("event_id", "count"),
                avg_length=("pass_length", "mean"),
            )
            .reset_index()
        )
        network["avg_length"] = network["avg_length"].round(1)
        return network.sort_values("pass_count", ascending=False)

    def compute_zone14_entries(self, events: pd.DataFrame, team_id: int = None) -> int:
        """Count entries into Zone 14 (central area just outside box)."""
        entries = events[
            (events["team_id"] == team_id)
            & (events["event_type"].isin(["Pass", "Carry"]))
            & (events["end_location_x"].between(self.ZONE14_X_MIN, self.ZONE14_X_MAX))
            & (events["end_location_y"].between(self.ZONE14_Y_MIN, self.ZONE14_Y_MAX))
        ]
        return len(entries)

    def compute_shot_zones(self, events: pd.DataFrame, team_id: int = None) -> pd.DataFrame:
        """Categorise shots into zones."""
        shots = events[
            (events["event_type"] == "Shot")
            & (events["team_id"] == team_id)
        ].copy()

        def classify_zone(row):
            x, y = row.get("location_x"), row.get("location_y")
            if pd.isna(x) or pd.isna(y):
                return "unknown"
            for zone, bounds in self.SHOT_ZONES.items():
                if bounds["x"][0] <= x <= bounds["x"][1] and bounds["y"][0] <= y <= bounds["y"][1]:
                    return zone
            return "long_range"

        shots["shot_zone"] = shots.apply(classify_zone, axis=1)
        return shots

    def compute_defensive_line_height(
        self, events: pd.DataFrame, team_id: int = None
    ) -> float:
        """Estimate defensive line height from defender positions."""
        defensive_actions = events[
            (events["team_id"] == team_id)
            & (events["event_type"].isin(["Tackle", "Interception", "Foul", "Clearance"]))
            & (events["location_x"].notna())
        ]

        if defensive_actions.empty:
            return 0.0

        # Average defensive action location = defensive line height
        avg_height = defensive_actions["location_x"].mean()
        return round(avg_height, 1)

    def compute_pass_progression_index(
        self, events: pd.DataFrame, team_id: int = None
    ) -> float:
        """Weighted measure of pass progression."""
        passes = events[
            (events["event_type"] == "Pass")
            & (events["team_id"] == team_id)
            & (events["location_x"].notna())
            & (events["end_location_x"].notna())
        ]

        if passes.empty:
            return 0.0

        passes["prog_distance"] = passes["end_location_x"] - passes["location_x"]
        progressive = passes[passes["prog_distance"] > 0]

        if progressive.empty:
            return 0.0

        # Weight shorter progressive passes higher, longer lower
        weights = 1 / (1 + np.exp(-(progressive["prog_distance"] - 10) / 5))
        index = (weights * progressive["prog_distance"]).sum()
        return round(index, 1)

    def extract_formation(self, events: pd.DataFrame) -> str:
        """Infer formation from average position clusters."""
        avg_pos = self.compute_average_positions(events)
        if avg_pos.empty:
            return "unknown"

        # Group players by y-coordinate bands
        defenders = avg_pos[avg_pos["avg_x"] < 40]
        midfielders = avg_pos[(avg_pos["avg_x"] >= 40) & (avg_pos["avg_x"] < 70)]
        forwards = avg_pos[avg_pos["avg_x"] >= 70]

        def_count = len(defenders)
        mid_count = len(midfielders)
        fwd_count = len(forwards)

        # Map to formation string
        if def_count >= 4 and mid_count >= 3 and fwd_count >= 2:
            return "4-3-3"
        elif def_count >= 4 and mid_count >= 2 and fwd_count >= 2:
            return "4-2-3-1" if fwd_count <= 2 else "4-2-4"
        elif def_count >= 3 and mid_count >= 4 and fwd_count >= 2:
            return "3-4-3"
        elif def_count >= 3 and mid_count >= 5 and fwd_count >= 1:
            return "3-5-2"
        elif def_count >= 4 and mid_count >= 4 and fwd_count >= 1:
            return "4-4-2"
        elif def_count >= 5 and mid_count >= 3 and fwd_count >= 1:
            return "5-3-2"
        elif def_count >= 5 and mid_count >= 4 and fwd_count >= 0:
            return "5-4-1"
        else:
            return f"{def_count}-{mid_count}-{fwd_count}"
