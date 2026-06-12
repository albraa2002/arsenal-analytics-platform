"""
Tactical dashboards — combinational views that integrate pitch plots
and analysis charts into dashboard-style outputs.
"""

from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.config import config
from config.logging_config import get_logger
from scripts.visualization.pitch_plots import PitchPlotter
from scripts.visualization.analysis_plots import AnalysisPlotter


class TacticalDashboard:
    """Multi-panel tactical dashboards combining pitch plots and analysis."""

    def __init__(self, logger_name: str = "tactical_dashboard"):
        self.logger = get_logger(logger_name)
        self.pitch_plotter = PitchPlotter()
        self.analysis_plotter = AnalysisPlotter()

    def match_dashboard(
        self,
        match_events: pd.DataFrame,
        home_team: str = "Arsenal",
        away_team: str = "Opponent",
        match_title: str = "Match Analysis",
        save_path: str = "",
    ) -> go.Figure:
        """Executive match dashboard with xG timeline, shot map, pass map."""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                "xG Timeline", "Shot Map", "Pass Network",
                "Possession", "Key Events", "Expected Goals",
            ),
            specs=[
                [{"type": "xy"}, {"type": "xy"}, {"type": "xy"}],
                [{"type": "domain"}, {"type": "xy"}, {"type": "domain"}],
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.08,
        )

        # xG Timeline (top-left)
        home_shots = match_events[match_events["team_name"] == home_team]
        away_shots = match_events[match_events["team_name"] == away_team]

        fig.add_trace(
            go.Bar(x=home_shots["minute"], y=home_shots["statsbomb_xg"],
                   name=home_team, marker_color="#EF0107"),
            row=1, col=1,
        )
        fig.add_trace(
            go.Bar(x=away_shots["minute"], y=away_shots["statsbomb_xg"],
                   name=away_team, marker_color="#00F0FF"),
            row=1, col=1,
        )

        # Shot Map placeholder — use mplsoccer for actual
        fig.add_annotation(
            row=1, col=2,
            text="See mplsoccer shot map output",
            showarrow=False,
            font=dict(color="#666"),
        )

        # Pass network placeholder
        fig.add_annotation(
            row=1, col=3,
            text="See mplsoccer pass map output",
            showarrow=False,
            font=dict(color="#666"),
        )

        # Possession pie (bottom-left)
        home_count = len(home_shots)
        away_count = len(away_shots)
        fig.add_trace(
            go.Pie(labels=[home_team, away_team],
                   values=[home_count, away_count],
                   marker_colors=["#EF0107", "#00F0FF"],
                   hole=0.4),
            row=2, col=1,
        )

        # Key events
        goals = match_events[match_events["shot_outcome"] == "Goal"]
        events_text = "<br>".join(
            f"{r['minute']}' — {r['player_name']} ({r['team_name']})"
            for _, r in goals.head(10).iterrows()
        ) or "No goals"
        fig.add_annotation(
            row=2, col=2,
            text=f"<b>Goals:</b><br>{events_text}",
            align="left",
            showarrow=False,
            font=dict(size=11, color="white"),
        )

        # xG totals
        total_xg_home = home_shots["statsbomb_xg"].sum()
        total_xg_away = away_shots["statsbomb_xg"].sum()
        fig.add_trace(
            go.Pie(
                labels=[f"{home_team} xG", f"{away_team} xG"],
                values=[total_xg_home, total_xg_away],
                marker_colors=["#EF0107", "#00F0FF"],
                hole=0.4,
                textinfo="label+percent",
            ),
            row=2, col=3,
        )

        fig.update_layout(
            title=dict(text=match_title, font=dict(size=22, color="white")),
            paper_bgcolor="#0D1117",
            plot_bgcolor="#0D1117",
            font=dict(color="#E6E6E6"),
            height=900,
            showlegend=False,
        )

        if save_path:
            full_path = config.paths.plots / save_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(full_path))
            self.logger.info(f"Dashboard saved: {full_path}")

        return fig

    def player_report(
        self,
        player_name: str,
        stats: Dict[str, float],
        percentiles: Dict[str, float],
        save_path: str = "",
    ) -> go.Figure:
        """Single-player comprehensive report with radar and metrics."""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(f"{player_name} — Percentile Rank", "Key Metrics"),
            specs=[[{"type": "polar"}, {"type": "bar"}]],
            column_widths=[0.5, 0.5],
        )

        categories = list(percentiles.keys())
        values = list(percentiles.values()) + [percentiles[list(percentiles.keys())[0]]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=player_name,
            line=dict(color="#EF0107", width=2),
            fillcolor="rgba(239, 1, 7, 0.2)",
        ), row=1, col=1)

        metrics = list(stats.keys())
        metric_values = list(stats.values())
        fig.add_trace(go.Bar(
            x=metrics,
            y=metric_values,
            marker_color="#00F0FF",
            name="Value",
        ), row=1, col=2)

        fig.update_layout(
            title=dict(text=f"Player Report: {player_name}", font=dict(size=20, color="white")),
            paper_bgcolor="#0D1117",
            plot_bgcolor="#0D1117",
            font=dict(color="#E6E6E6", family="Cairo"),
            polar=dict(
                bgcolor="rgba(13, 17, 23, 0.8)",
                angularaxis=dict(color="#E6E6E6", gridcolor="#1A2332"),
                radialaxis=dict(color="#E6E6E6", gridcolor="#1A2332", range=[0, 100]),
            ),
            height=600,
            showlegend=False,
        )

        if save_path:
            full_path = config.paths.plots / save_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(str(full_path))
            self.logger.info(f"Player report saved: {full_path}")

        return fig
