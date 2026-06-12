"""
Tactical Analysis — passing networks, average positions, heatmaps,
zone 14 entries, progressive passes, and pressing intensity.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from mplsoccer import Pitch, FontManager, add_image
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data" / "final"

# ── Style ──
DARK_BG = "#060B18"
GRID_COLOR = "#1A2332"
ARSENAL_RED = "#EF0107"
NEON_CYAN = "#00F5FF"
TEXT_COLOR = "#8892B0"

st.markdown("<h2>🧠 Tactical Analysis</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8892B0;'>Passing networks · Average positions · Heatmaps · Pressing intensity</p>", unsafe_allow_html=True)
st.markdown("---")


@st.cache_data
def load():
    files = {
        "matches": "fact_matches.csv",
        "player_stats": "fact_player_match_stats.csv",
        "shots": "fact_shots.csv",
    }
    data = {}
    for key, fname in files.items():
        p = DATA_DIR / fname
        data[key] = pd.read_csv(p) if p.exists() else pd.DataFrame()
    return data


d = load()
df_ps = d["player_stats"]
df_m = d["matches"]

st.info("ℹ️ Tactical visualizations use synthetic data for demonstration. Connect real StatsBomb event data for production use.", icon="ℹ️")

# ── Generate synthetic tactical data ──
np.random.seed(42)

def gen_pass_data(n=100):
    players = ["Saka", "Odegaard", "Rice", "Havertz", "Martinelli",
               "White", "Saliba", "Gabriel", "Zinchenko", "Partey", "Trossard"]
    passes = []
    for _ in range(n):
        src = np.random.choice(players)
        tgt = np.random.choice([p for p in players if p != src])
        passes.append({
            "player": src,
            "recipient": tgt,
            "x": np.random.uniform(10, 110),
            "y": np.random.uniform(5, 75),
            "end_x": np.random.uniform(10, 110),
            "end_y": np.random.uniform(5, 75),
            "length": np.random.uniform(5, 40),
        })
    return pd.DataFrame(passes)

def gen_positions():
    players = {
        "Raya": (5, 34), "White": (20, 55), "Saliba": (20, 40), "Gabriel": (20, 28),
        "Zinchenko": (20, 12), "Rice": (38, 45), "Odegaard": (42, 34), "Partey": (38, 22),
        "Saka": (58, 55), "Havertz": (60, 34), "Martinelli": (58, 12),
    }
    return pd.DataFrame([
        {"player": k, "avg_x": v[0] + np.random.normal(0, 3), "avg_y": v[1] + np.random.normal(0, 3),
         "touch_count": np.random.randint(30, 90)}
        for k, v in players.items()
    ])

def gen_events(n=300):
    events = []
    for _ in range(n):
        events.append({
            "x": np.random.uniform(0, 120),
            "y": np.random.uniform(0, 80),
            "type": np.random.choice(["Pass", "Carry", "Tackle", "Pressure", "Shot"],
                                     p=[0.5, 0.2, 0.1, 0.15, 0.05]),
        })
    return pd.DataFrame(events)


# ── Row 1: Passing Network + Average Positions ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='glass-card'><h3>🔄 Passing Network</h3>", unsafe_allow_html=True)
    pass_df = gen_pass_data(150)

    pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                  line_color=GRID_COLOR, linewidth=1.5, axis=False, label=False)
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)

    for _, p in pass_df.iterrows():
        pitch.arrows(
            p["x"], p["y"], p["end_x"], p["end_y"],
            ax=ax, color=ARSENAL_RED, alpha=0.2, width=1.5,
            headwidth=4, headlength=4,
        )

    connection_counts = pass_df.groupby("player").size().sort_values(ascending=False)
    pos_data = gen_positions()
    for _, pl in pos_data.iterrows():
        size = max(connection_counts.get(pl["player"], 30) * 0.8, 30)
        pitch.scatter(pl["avg_x"], pl["avg_y"], s=size, ax=ax,
                      color=NEON_CYAN, edgecolors="white", linewidth=1.5, alpha=0.85, zorder=5)
        ax.annotate(
            pl["player"], (pl["avg_x"], pl["avg_y"]),
            xytext=(0, -18), textcoords="offset points",
            color="white", fontsize=7, ha="center", fontfamily="monospace",
        )

    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'><h3>📍 Average Positions (4-3-3)</h3>", unsafe_allow_html=True)
    pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                  line_color=GRID_COLOR, linewidth=1.5, axis=False, label=False)
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)

    pos_data = gen_positions()
    for _, pl in pos_data.iterrows():
        pitch.scatter(pl["avg_x"], pl["avg_y"], s=pl["touch_count"] * 0.8,
                      ax=ax, color=ARSENAL_RED, edgecolors="white",
                      linewidth=1.5, alpha=0.8, zorder=5)
        ax.annotate(
            pl["player"], (pl["avg_x"], pl["avg_y"]),
            xytext=(0, -18), textcoords="offset points",
            color="white", fontsize=7, ha="center", fontfamily="monospace",
        )

    # Formation zones
    ax.axvspan(0, 25, alpha=0.03, color=NEON_CYAN, zorder=0)
    ax.axvspan(25, 55, alpha=0.03, color="white", zorder=0)
    ax.axvspan(55, 80, alpha=0.03, color=NEON_CYAN, zorder=0)
    ax.axvspan(80, 120, alpha=0.03, color=ARSENAL_RED, zorder=0)

    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 2: Heatmap + Pressing Intensity ──
col3, col4 = st.columns(2)

with col3:
    st.markdown("<div class='glass-card'><h3>🔥 Event Heatmap</h3>", unsafe_allow_html=True)
    events = gen_events(500)

    pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                  line_color=GRID_COLOR, linewidth=1.5, axis=False, label=False)
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)

    x = events["x"].values
    y = events["y"].values
    pitch.kdeplot(x, y, ax=ax, cmap="hot", fill=True, levels=50, alpha=0.7, shade=True)

    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='glass-card'><h3>⚡ Pressing Intensity</h3>", unsafe_allow_html=True)
    pressures = gen_events(200)
    pressures = pressures[pressures["type"] == "Pressure"]

    pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                  line_color=GRID_COLOR, linewidth=1.5, axis=False, label=False)
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)

    if not pressures.empty:
        x = pressures["x"].values
        y = pressures["y"].values
        pitch.kdeplot(x, y, ax=ax, cmap="viridis", fill=True, levels=30, alpha=0.6, shade=True)
        pitch.scatter(x, y, s=15, ax=ax, color=NEON_CYAN, alpha=0.4, edgecolors="none")

    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: Tactical Bar Charts ──
col5, col6, col7 = st.columns(3)

with col5:
    st.markdown("<div class='glass-card'><h3>📊 Progressive Passes by Player</h3>", unsafe_allow_html=True)
    players = ["Odegaard", "Rice", "Saka", "White", "Zinchenko", "Partey", "Martinelli", "Havertz"]
    prog_passes = np.random.randint(3, 15, len(players))
    df_prog = pd.DataFrame({"Player": players, "Progressive Passes": prog_passes}).sort_values("Progressive Passes")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_prog["Player"], x=df_prog["Progressive Passes"],
        orientation="h", marker_color=ARSENAL_RED,
        text=df_prog["Progressive Passes"], textposition="outside",
        marker_line=dict(color=NEON_CYAN, width=1),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=350,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col6:
    st.markdown("<div class='glass-card'><h3>🎯 Zone 14 Entries</h3>", unsafe_allow_html=True)
    matches = [f"M{i}" for i in range(1, 11)]
    entries = np.random.randint(5, 25, 10)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=matches, y=entries,
        mode="lines+markers",
        line=dict(color=NEON_CYAN, width=3),
        marker=dict(size=10, color=NEON_CYAN, line=dict(color="white", width=1)),
        fill="tozeroy", fillcolor="rgba(0,245,255,0.08)",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=350,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(title="Entries", gridcolor=GRID_COLOR),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col7:
    st.markdown("<div class='glass-card'><h3>🛡️ PPDA by Match</h3>", unsafe_allow_html=True)
    ppda_vals = np.random.uniform(8, 16, 10)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=matches, y=ppda_vals,
        marker_color=np.where(ppda_vals < 11, "#00D4AA", np.where(ppda_vals < 13, "#FFB347", "#FF4757")),
        text=[f"{v:.1f}" for v in ppda_vals],
        textposition="outside",
        hovertemplate="Match %{x}<br>PPDA: %{y:.1f}<extra></extra>",
    ))
    fig.add_hline(y=11, line_dash="dash", line_color="#00D4AA", annotation_text="Good pressing")
    fig.add_hline(y=13, line_dash="dash", line_color="#FF4757", annotation_text="Poor pressing")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=350,
        xaxis=dict(gridcolor=GRID_COLOR),
        yaxis=dict(title="PPDA", gridcolor=GRID_COLOR),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
