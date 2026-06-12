"""
Pitch visualizations using mplsoccer — heatmaps, pass maps, shot maps,
and average position plots.
"""

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from mplsoccer import Pitch, VerticalPitch, FontManager, add_image

from config.config import config
from config.logging_config import get_logger


class PitchPlotter:
    """Renders football-pitch visualisations with mplsoccer."""

    ARSENAL_RED: str = "#EF0107"
    ARSENAL_GOLD: str = "#9C824A"
    NAVY: str = "#0A1C3E"
    NEON_CYAN: str = "#00F0FF"
    DARK_BG: str = "#0D1117"
    GRID_COLOR: str = "#1A2332"

    def __init__(self, logger_name: str = "pitch_plotter"):
        self.logger = get_logger(logger_name)
        self.pitch = Pitch(
            pitch_type="statsbomb",
            pitch_color=self.DARK_BG,
            line_color=self.GRID_COLOR,
            linewidth=1.5,
            axis=False,
            label=False,
        )
        self.fig = None
        self.ax = None

    def _setup_figure(self, title: str = ""):
        self.fig, self.ax = self.pitch.draw(figsize=(14, 10))
        self.fig.patch.set_facecolor(self.DARK_BG)
        if title:
            self.ax.set_title(
                title, color="white", fontsize=16,
                fontfamily="sans-serif", pad=20,
            )
        return self.fig, self.ax

    def plot_shot_map(
        self,
        shots: pd.DataFrame,
        title: str = "Shot Map",
        team_color: str = None,
        save_path: str = "",
    ) -> plt.Figure:
        self._setup_figure(title)
        color = team_color or self.ARSENAL_RED

        for _, shot in shots.iterrows():
            x = shot.get("location_x", 0)
            y = shot.get("location_y", 0)
            xg = shot.get("statsbomb_xg", 0.1)
            goal = shot.get("shot_outcome", "") == "Goal"

            marker_size = max(np.sqrt(xg) * 50, 50)
            edge_color = self.ARSENAL_GOLD if goal else color
            self.pitch.scatter(
                x, y, s=marker_size, ax=self.ax,
                color=color, edgecolors=edge_color,
                linewidth=2, alpha=0.7, zorder=5,
            )
            if goal:
                self.pitch.scatter(
                    x, y, s=marker_size + 20, ax=self.ax,
                    color="none", edgecolors=self.ARSENAL_GOLD,
                    linewidth=3, alpha=0.8, zorder=4,
                )

        legend = [
            mpatches.Patch(color=color, label=f"Shots ({len(shots)})"),
            mpatches.Patch(color=self.ARSENAL_GOLD, label="Goal"),
        ]
        self.ax.legend(
            handles=legend, loc="upper right",
            facecolor=self.DARK_BG, edgecolor=self.GRID_COLOR,
            labelcolor="white", fontsize=10,
        )

        if save_path:
            self._save(save_path)
        return self.fig

    def plot_pass_map(
        self,
        passes: pd.DataFrame,
        title: str = "Pass Map",
        team_color: str = None,
        arrow_alpha: float = 0.3,
        save_path: str = "",
    ) -> plt.Figure:
        self._setup_figure(title)
        color = team_color or self.ARSENAL_RED

        for _, p in passes.iterrows():
            x, y = p.get("location_x", 0), p.get("location_y", 0)
            ex, ey = p.get("end_location_x", 0), p.get("end_location_y", 0)
            if pd.notna(x) and pd.notna(y) and pd.notna(ex) and pd.notna(ey):
                self.pitch.arrows(
                    x, y, ex, ey, ax=self.ax,
                    color=color, alpha=arrow_alpha,
                    width=1.5, headwidth=4, headlength=4,
                )

        completed = passes[passes.get("pass_outcome", "") != "Incomplete"]
        missed = passes[passes.get("pass_outcome", "") == "Incomplete"]
        legend = [
            mpatches.Patch(color=color, label=f"Complete ({len(completed)})"),
            mpatches.Patch(color=self.ARSENAL_GOLD, label=f"Missed ({len(missed)})"),
        ]
        self.ax.legend(
            handles=legend, loc="upper right",
            facecolor=self.DARK_BG, edgecolor=self.GRID_COLOR,
            labelcolor="white", fontsize=10,
        )

        if save_path:
            self._save(save_path)
        return self.fig

    def plot_heatmap(
        self,
        events: pd.DataFrame,
        title: str = "Event Heatmap",
        cmap: str = "plasma",
        save_path: str = "",
    ) -> plt.Figure:
        self._setup_figure(title)
        x = events["location_x"].dropna()
        y = events["location_y"].dropna()
        self.pitch.kdeplot(
            x, y, ax=self.ax,
            cmap=cmap, fill=True,
            levels=50, alpha=0.8,
            shade=True,
        )
        if save_path:
            self._save(save_path)
        return self.fig

    def plot_average_positions(
        self,
        positions: pd.DataFrame,
        title: str = "Average Positions",
        team_color: str = None,
        save_path: str = "",
    ) -> plt.Figure:
        self._setup_figure(title)
        color = team_color or self.ARSENAL_RED

        positions = positions.sort_values("avg_x", ascending=True)
        for _, row in positions.iterrows():
            self.pitch.scatter(
                row["avg_x"], row["avg_y"],
                s=row.get("touch_count", 50) * 2,
                ax=self.ax, color=color,
                edgecolors="white", linewidth=1.5, alpha=0.8, zorder=5,
            )
            self.ax.annotate(
                row.get("player_name", ""),
                (row["avg_x"], row["avg_y"]),
                xytext=(0, -20), textcoords="offset points",
                color="white", fontsize=8, ha="center",
                fontfamily="monospace",
            )

        if save_path:
            self._save(save_path)
        return self.fig

    def _save(self, path: str):
        full_path = config.paths.plots / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(
            str(full_path), dpi=200, bbox_inches="tight",
            facecolor=self.DARK_BG, edgecolor="none",
        )
        plt.close(self.fig)
        self.logger.info(f"Plot saved: {full_path}")
