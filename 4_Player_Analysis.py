"""
Player Analysis — interactive player selector with radar chart,
per-90 metrics, shot map, and heatmap.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from mplsoccer import Pitch
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data" / "final"

DARK_BG = "#060B18"
GRID_COLOR = "#1A2332"
ARSENAL_RED = "#EF0107"
NEON_CYAN = "#00F5FF"
TEXT_COLOR = "#8892B0"
GOLD = "#9C824A"

st.markdown("<h2>👤 Player Analysis</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8892B0;'>Deep dive into individual performance · Radar charts · Per-90 metrics</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Arsenal squad with synthetic stats ──
np.random.seed(42)
SQUAD = {
    "Raya": {"pos": "GK", "age": 29, "apps": 35, "minutes": 3150},
    "White": {"pos": "DF", "age": 27, "apps": 33, "minutes": 2850},
    "Saliba": {"pos": "DF", "age": 24, "apps": 34, "minutes": 3000},
    "Gabriel": {"pos": "DF", "age": 27, "apps": 32, "minutes": 2880},
    "Zinchenko": {"pos": "DF", "age": 28, "apps": 28, "minutes": 2200},
    "Timber": {"pos": "DF", "age": 23, "apps": 20, "minutes": 1500},
    "Partey": {"pos": "MF", "age": 31, "apps": 25, "minutes": 1850},
    "Rice": {"pos": "MF", "age": 25, "apps": 34, "minutes": 3000},
    "Odegaard": {"pos": "MF", "age": 26, "apps": 33, "minutes": 2850},
    "Havertz": {"pos": "MF", "age": 25, "apps": 30, "minutes": 2400},
    "Saka": {"pos": "FW", "age": 23, "apps": 34, "minutes": 2950},
    "Martinelli": {"pos": "FW", "age": 23, "apps": 30, "minutes": 2400},
    "Trossard": {"pos": "FW", "age": 30, "apps": 28, "minutes": 1800},
    "Jesus": {"pos": "FW", "age": 28, "apps": 22, "minutes": 1500},
    "Nwaneri": {"pos": "MF", "age": 18, "apps": 15, "minutes": 600},
    "Lewis-Skelly": {"pos": "DF", "age": 18, "apps": 12, "minutes": 450},
    "Calafiori": {"pos": "DF", "age": 22, "apps": 18, "minutes": 1200},
}


def gen_player_stats():
    stats = {}
    for name, info in SQUAD.items():
        mins = max(info["minutes"], 90)
        factor = mins / 3800
        stats[name] = {
            "xG_90": round(np.random.uniform(0.05, 0.55) * (1.5 if info["pos"] in ("FW", "MF") else 0.6), 2),
            "xA_90": round(np.random.uniform(0.02, 0.4) * (1.3 if info["pos"] in ("FW", "MF") else 0.5), 2),
            "prog_passes_90": round(np.random.uniform(2, 12) * factor, 1),
            "prog_carries_90": round(np.random.uniform(1, 8) * factor, 1),
            "touches_90": round(np.random.uniform(30, 90) * factor, 0),
            "pass_pct": round(np.random.uniform(72, 94), 1),
            "tackles_90": round(np.random.uniform(0.5, 4) * (1.2 if info["pos"] in ("DF", "MF") else 0.4), 1),
            "interceptions_90": round(np.random.uniform(0.3, 2.5) * (1.2 if info["pos"] in ("DF", "MF") else 0.3), 1),
            "def_actions_90": round(np.random.uniform(2, 8) * (1.3 if info["pos"] in ("DF", "MF") else 0.3), 1),
            "goals": np.random.randint(0, 20) if info["pos"] in ("FW", "MF") else np.random.randint(0, 5),
            "assists": np.random.randint(0, 12) if info["pos"] in ("FW", "MF") else np.random.randint(0, 4),
            "shots_90": round(np.random.uniform(0.3, 4) * (1.5 if info["pos"] in ("FW", "MF") else 0.3), 1),
            "key_passes_90": round(np.random.uniform(0.2, 3) * (1.3 if info["pos"] in ("FW", "MF") else 0.5), 1),
        }
    return stats


player_stats = gen_player_stats()


# ── Player selector ──
players_list = list(SQUAD.keys())

# Sidebar is already set up in app.py; use an inline selector
col_sel, col_info = st.columns([1, 2])

with col_sel:
    st.markdown("<div class='glass-card'><h3>👤 Select Player</h3>", unsafe_allow_html=True)
    selected_player = st.selectbox("", players_list, index=players_list.index("Saka"), label_visibility="collapsed")
    info = SQUAD[selected_player]
    stats = player_stats[selected_player]
    st.markdown("</div>", unsafe_allow_html=True)

with col_info:
    st.markdown(
        f"<div class='glass-card' style='text-align:center;'>"
        f"<h2 style='margin-bottom:4px;'>{selected_player}</h2>"
        f"<p style='color:{NEON_CYAN};letter-spacing:3px;text-transform:uppercase;font-size:0.9rem;'>{info['pos']} · Age {info['age']}</p>"
        f"<div style='display:flex;justify-content:center;gap:40px;margin-top:16px;'>"
        f"<div><span style='color:{ARSENAL_RED};font-size:2rem;font-family:IBM Plex Mono;font-weight:700;'>{info['apps']}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Appearances</span></div>"
        f"<div><span style='color:{ARSENAL_RED};font-size:2rem;font-family:IBM Plex Mono;font-weight:700;'>{info['minutes']}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Minutes</span></div>"
        f"<div><span style='color:{ARSENAL_RED};font-size:2rem;font-family:IBM Plex Mono;font-weight:700;'>{stats['goals']}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Goals</span></div>"
        f"<div><span style='color:{ARSENAL_RED};font-size:2rem;font-family:IBM Plex Mono;font-weight:700;'>{stats['assists']}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Assists</span></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Row 1: Radar + Per-90 Metrics ──
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='glass-card'><h3>📊 Player Radar</h3>", unsafe_allow_html=True)

    # Get comparison player (league average or another player)
    comparison_name = "Odegaard" if selected_player != "Odegaard" else "Rice"
    comparison_stats = player_stats[comparison_name]

    categories = ["xG/90", "xA/90", "Prog Passes", "Prog Carries",
                  "Touches/90", "Pass %", "Tackles/90", "Def Actions"]
    radar_map = {
        "xG/90": "xG_90", "xA/90": "xA_90",
        "Prog Passes": "prog_passes_90", "Prog Carries": "prog_carries_90",
        "Touches/90": "touches_90", "Pass %": "pass_pct",
        "Tackles/90": "tackles_90", "Def Actions": "def_actions_90",
    }
    player_vals = [stats[radar_map[c]] for c in categories]
    comp_vals = [comparison_stats[radar_map[c]] for c in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=player_vals + [player_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=selected_player,
        line=dict(color=ARSENAL_RED, width=2),
        fillcolor="rgba(239,1,7,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=comp_vals + [comp_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=comparison_name,
        line=dict(color=NEON_CYAN, width=2),
        fillcolor="rgba(0,245,255,0.1)",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR),
        polar=dict(
            bgcolor="rgba(13,17,23,0.5)",
            angularaxis=dict(color=TEXT_COLOR, gridcolor=GRID_COLOR),
            radialaxis=dict(color=TEXT_COLOR, gridcolor=GRID_COLOR, showticklabels=False),
        ),
        height=450,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'><h3>📊 Per-90 Metrics</h3>", unsafe_allow_html=True)

    metrics_table = [
        ("🎯 xG/90", f"{stats['xG_90']:.2f}", "Expected goals per 90"),
        ("🎯 xA/90", f"{stats['xA_90']:.2f}", "Expected assists per 90"),
        ("📤 Prog Passes/90", f"{stats['prog_passes_90']}", "Progressive passes per 90"),
        ("🏃 Prog Carries/90", f"{stats['prog_carries_90']}", "Progressive carries per 90"),
        ("👟 Touches/90", f"{stats['touches_90']:.0f}", "Total touches per 90"),
        ("📨 Pass Completion %", f"{stats['pass_pct']}%", "Pass accuracy"),
        ("🛡️ Tackles/90", f"{stats['tackles_90']:.1f}", "Tackles per 90"),
        ("✋ Interceptions/90", f"{stats['interceptions_90']:.1f}", "Interceptions per 90"),
        ("⚔️ Def Actions/90", f"{stats['def_actions_90']:.1f}", "Defensive actions per 90"),
        ("⚽ Shots/90", f"{stats['shots_90']:.1f}", "Shots per 90"),
        ("🔑 Key Passes/90", f"{stats['key_passes_90']:.1f}", "Key passes per 90"),
    ]

    for icon, val, desc in metrics_table:
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);'>"
            f"<span style='color:{TEXT_COLOR};font-size:0.9rem;'>{icon} {desc}</span>"
            f"<span style='color:white;font-family:IBM Plex Mono;font-weight:600;font-size:1.1rem;'>{val}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 2: Shot Map + Heatmap ──
col3, col4 = st.columns(2)

with col3:
    st.markdown("<div class='glass-card'><h3>🎯 Shot Map — {}</h3>".format(selected_player), unsafe_allow_html=True)
    n_shots = np.random.randint(15, 40)
    pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                  line_color=GRID_COLOR, linewidth=1.5, axis=False, label=False)
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)

    for _ in range(n_shots):
        x, y = np.random.uniform(75, 118), np.random.uniform(8, 62)
        xg = np.random.exponential(0.12)
        goal = np.random.random() < 0.12
        size = max(np.sqrt(xg) * 60, 25)
        edge = "#FFD700" if goal else ARSENAL_RED
        pitch.scatter(x, y, s=size, ax=ax, color=ARSENAL_RED,
                      edgecolors=edge, linewidth=2, alpha=0.7, zorder=5)
        if goal:
            ax.annotate("⚽", (x, y), fontsize=12, ha="center", va="center")

    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='glass-card'><h3>🔥 Touch Heatmap — {}</h3>".format(selected_player), unsafe_allow_html=True)
    n_events = np.random.randint(100, 300)

    pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                  line_color=GRID_COLOR, linewidth=1.5, axis=False, label=False)
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)

    x_events = np.random.uniform(0, 120, n_events)
    y_events = np.random.uniform(0, 80, n_events)

    if info["pos"] == "GK":
        x_events = np.random.uniform(0, 25, n_events)
        y_events = np.random.uniform(20, 60, n_events)
    elif info["pos"] == "DF":
        x_events = np.random.uniform(5, 55, n_events)
        y_events = np.random.uniform(5, 75, n_events)
    elif info["pos"] == "MF":
        x_events = np.random.uniform(20, 85, n_events)
        y_events = np.random.uniform(5, 75, n_events)
    elif info["pos"] == "FW":
        x_events = np.random.uniform(40, 115, n_events)
        y_events = np.random.uniform(10, 70, n_events)

    pitch.kdeplot(x_events, y_events, ax=ax, cmap="hot",
                  fill=True, levels=40, alpha=0.7, shade=True)

    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: Performance Trend ──
st.markdown("<div class='glass-card'><h3>📈 Performance Trend (Rolling 5-match)</h3>", unsafe_allow_html=True)
weeks = list(range(1, 21))
np.random.seed(hash(selected_player) % (2**31))
trend_xg = np.random.uniform(0.1, 0.8, 20).cumsum()
trend_xa = np.random.uniform(0.05, 0.5, 20).cumsum()
trend_mins = np.random.uniform(60, 95, 20)

fig = make_subplots(rows=1, cols=1)
fig.add_trace(go.Scatter(
    x=weeks, y=np.convolve(trend_xg / np.arange(1, 21), np.ones(5)/5, mode="same"),
    mode="lines+markers", name="xG/90 (rolling)",
    line=dict(color=ARSENAL_RED, width=3),
    marker=dict(size=8, color=ARSENAL_RED),
))
fig.add_trace(go.Scatter(
    x=weeks, y=np.convolve(trend_xa / np.arange(1, 21), np.ones(5)/5, mode="same"),
    mode="lines+markers", name="xA/90 (rolling)",
    line=dict(color=NEON_CYAN, width=3),
    marker=dict(size=8, color=NEON_CYAN),
))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_COLOR), height=350,
    xaxis=dict(title="Gameweek", gridcolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR),
    hovermode="x unified",
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
