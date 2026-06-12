"""
Analysis visualizations — xG timelines, radar charts, bar charts,
and statistical plots using Plotly.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.config import config
from config.logging_config import get_logger


class AnalysisPlotter:
    """Plotly-based analysis plots with dark theme."""

    DARK_TEMPLATE = {
        "layout": {
            "paper_bgcolor": "#0D1117",
            "plot_bgcolor": "#0D1117",
            "font": {"color": "#E6E6E6", "family": "Cairo, sans-serif"},
            "title": {"font": {"color": "#FFFFFF", "size": 20}},
            "xaxis": {"gridcolor": "#1A2332", "zerolinecolor": "#1A2332"},
            "yaxis": {"gridcolor": "#1A2332", "zerolinecolor": "#1A2332"},
            "legend": {"bgcolor": "rgba(0,0,0,0)", "font": {"color": "#E6E6E6"}},
        }
    }

    ARSENAL_RED = "#EF0107"
    NEON_CYAN = "#00F0FF"
    NAVY = "#0A1C3E"
    GOLD = "#9C824A"

    def __init__(self, logger_name: str = "analysis_plots"):
        self.logger = get_logger(logger_name)

    def plot_xg_timeline(
        self,
        match_events: pd.DataFrame,
        home_team: str = "Arsenal",
        away_team: str = "Opponent",
        title: str = "xG Timeline",
        save_path: str = "",
    ) -> go.Figure:
        fig = go.Figure()

        home_shots = match_events[match_events["team_name"] == home_team]
        away_shots = match_events[match_events["team_name"] == away_team]

        fig.add_trace(go.Bar(
            x=home_shots["minute"],
            y=home_shots["statsbomb_xg"],
            name=home_team,
            marker_color=self.ARSENAL_RED,
            opacity=0.8,
            hovertemplate="Min %{x}<br>xG: %{y:.2f}<extra></extra>",
        ))

        fig.add_trace(go.Bar(
            x=away_shots["minute"],
            y=away_shots["statsbomb_xg"],
            name=away_team,
            marker_color=self.NEON_CYAN,
            opacity=0.6,
            hovertemplate="Min %{x}<br>xG: %{y:.2f}<extra></extra>",
        ))

        # Cumulative xG lines
        home_shots_sorted = home_shots.sort_values("minute")
        away_shots_sorted = away_shots.sort_values("minute")
        if not home_shots_sorted.empty:
            home_cum = home_shots_sorted["statsbomb_xg"].cumsum()
            fig.add_trace(go.Scatter(
                x=home_shots_sorted["minute"], y=home_cum,
                mode="lines", name=f"{home_team} (cum)",
                line=dict(color=self.ARSENAL_RED, width=2, dash="dot"),
            ))
        if not away_shots_sorted.empty:
            away_cum = away_shots_sorted["statsbomb_xg"].cumsum()
            fig.add_trace(go.Scatter(
                x=away_shots_sorted["minute"], y=away_cum,
                mode="lines", name=f"{away_team} (cum)",
                line=dict(color=self.NEON_CYAN, width=2, dash="dot"),
            ))

        fig.update_layout(
            title=title, **self.DARK_TEMPLATE["layout"],
            xaxis_title="Minute", yaxis_title="xG",
            barmode="overlay", hovermode="x unified",
            height=500,
        )

        if save_path:
            self._save_html(fig, save_path)
        return fig

    def plot_radar(
        self,
        player_stats: Dict[str, float],
        comparison_stats: Dict[str, float] = None,
        player_name: str = "Player",
        comparison_name: str = "Comparison",
        title: str = "Player Radar",
        save_path: str = "",
    ) -> go.Figure:
        categories = list(player_stats.keys())
        values = list(player_stats.values())
        values += values[:1]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=player_name,
            line=dict(color=self.ARSENAL_RED, width=2),
            fillcolor=f"rgba(239, 1, 7, 0.2)",
        ))

        if comparison_stats:
            comp_values = list(comparison_stats.values())
            comp_values += comp_values[:1]
            fig.add_trace(go.Scatterpolar(
                r=comp_values,
                theta=categories + [categories[0]],
                fill="toself",
                name=comparison_name,
                line=dict(color=self.NEON_CYAN, width=2),
                fillcolor=f"rgba(0, 240, 255, 0.15)",
            ))

        fig.update_layout(
            title=title, **self.DARK_TEMPLATE["layout"],
            polar=dict(
                bgcolor="rgba(13, 17, 23, 0.8)",
                angularaxis=dict(color="#E6E6E6", linecolor="#1A2332"),
                radialaxis=dict(color="#E6E6E6", gridcolor="#1A2332"),
            ),
            height=600,
        )

        if save_path:
            self._save_html(fig, save_path)
        return fig

    def plot_player_comparison(
        self,
        players_df: pd.DataFrame,
        metrics: List[str],
        title: str = "Player Comparison",
        save_path: str = "",
    ) -> go.Figure:
        n = len(metrics)
        fig = make_subplots(
            rows=1, cols=n,
            subplot_titles=metrics,
            specs=[[{"type": "bar"} for _ in range(n)]],
        )

        colors = px.colors.qualitative.Set1
        for i, metric in enumerate(metrics):
            sorted_df = players_df.sort_values(metric, ascending=True)
            fig.add_trace(
                go.Bar(
                    y=sorted_df["player_name"],
                    x=sorted_df[metric],
                    orientation="h",
                    marker_color=colors[i % len(colors)],
                    showlegend=False,
                    hovertemplate=f"%{{y}}: %{{x:.2f}}<extra></extra>",
                ),
                row=1, col=i + 1,
            )

        fig.update_layout(
            title=title, **self.DARK_TEMPLATE["layout"],
            height=400 + 30 * len(players_df),
            barmode="group",
        )

        if save_path:
            self._save_html(fig, save_path)
        return fig

    def plot_performance_trend(
        self,
        time_series: pd.DataFrame,
        date_col: str = "date",
        value_col: str = "value",
        player_col: str = "player_name",
        title: str = "Performance Trend",
        save_path: str = "",
    ) -> go.Figure:
        fig = go.Figure()

        for player in time_series[player_col].unique():
            player_data = time_series[time_series[player_col] == player]
            fig.add_trace(go.Scatter(
                x=player_data[date_col],
                y=player_data[value_col],
                mode="lines+markers",
                name=player,
                line=dict(width=2),
                marker=dict(size=6),
            ))

        fig.update_layout(
            title=title, **self.DARK_TEMPLATE["layout"],
            xaxis_title="Date", yaxis_title=value_col,
            hovermode="x unified", height=500,
        )

        if save_path:
            self._save_html(fig, save_path)
        return fig

    def plot_value_chart(
        self,
        players: pd.DataFrame,
        price_col: str = "now_cost",
        points_col: str = "total_points",
        label_col: str = "web_name",
        title: str = "FPL Value Chart",
        save_path: str = "",
    ) -> go.Figure:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=players[price_col],
            y=players[points_col],
            mode="markers+text",
            text=players[label_col],
            textposition="top center",
            marker=dict(
                size=np.sqrt(players.get("selected_by_percent", 5)) * 3,
                color=self.ARSENAL_RED,
                line=dict(color="white", width=1),
            ),
            hovertemplate="<b>%{text}</b><br>"
                          f"Price: %{{x}}<br>"
                          f"Points: %{{y}}<extra></extra>",
        ))

        fig.update_layout(
            title=title, **self.DARK_TEMPLATE["layout"],
            xaxis_title="Price (£m)", yaxis_title="Total Points",
            height=600,
        )

        if save_path:
            self._save_html(fig, save_path)
        return fig

    def _save_html(self, fig: go.Figure, path: str):
        full_path = config.paths.plots / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(full_path))
        self.logger.info(f"Plot saved: {full_path}")
