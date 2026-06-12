"""
Match Analysis — interactive match selector with xG timeline,
shot maps, momentum chart, and tactical events.
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

st.markdown("<h2>🎯 Match Analysis</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8892B0;'>Interactive match selector with xG timeline · Shot maps · Momentum</p>", unsafe_allow_html=True)
st.markdown("---")


def load():
    p = DATA_DIR / "fact_matches.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


df = load()

if df.empty:
    st.warning("No match data available.")
    st.stop()

# Generate synthetic match names
if "match_id" in df.columns:
    df["match_label"] = df.apply(
        lambda r: f"Match {r['match_id']}" if pd.notna(r.get("match_id")) else f"M{np.random.randint(1, 39)}",
        axis=1,
    )
else:
    df["match_label"] = [f"Match {i+1}" for i in range(len(df))]

match_options = df["match_label"].tolist()

col_sel, col_info = st.columns([1, 2])

with col_sel:
    st.markdown("<div class='glass-card'><h3>🎮 Select Match</h3>", unsafe_allow_html=True)
    selected = st.selectbox("", match_options, index=len(match_options) - 1, label_visibility="collapsed")
    match_row = df[df["match_label"] == selected].iloc[0] if len(df) > 0 else None
    st.markdown("</div>", unsafe_allow_html=True)

with col_info:
    if match_row is not None:
        home_score = int(match_row.get("home_score", 0))
        away_score = int(match_row.get("away_score", 0))
        home_team = "Arsenal"
        away_team = match_row.get("away_team_name", "Opponent")

        result_class = "badge-win" if home_score > away_score else ("badge-draw" if home_score == away_score else "badge-loss")
        result_text = "WIN" if home_score > away_score else ("DRAW" if home_score == away_score else "LOSS")

        st.markdown(
            f"<div class='glass-card' style='text-align:center;'>"
            f"<h3 style='margin-bottom:8px;'>{home_team} vs {away_team}</h3>"
            f"<div style='font-size:3rem;font-family:IBM Plex Mono;font-weight:700;'>"
            f"{home_score} - {away_score}"
            f"</div>"
            f"<span class='{result_class}' style='font-size:1.2rem;padding:6px 20px;margin-top:8px;'>{result_text}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Generate synthetic per-match data ──
np.random.seed(42 if selected else 0)
n_shots_home = np.random.randint(8, 20)
n_shots_away = np.random.randint(5, 15)


def gen_shot_data(n, team):
    shots = []
    for _ in range(n):
        xg = np.random.exponential(0.15)
        shots.append({
            "minute": np.random.randint(1, 96),
            "xG": min(xg, 0.95),
            "goal": np.random.random() < 0.1,
            "team": team,
            "x": np.random.uniform(75, 118),
            "y": np.random.uniform(8, 62),
            "body_part": np.random.choice(["Right Foot", "Left Foot", "Head"], p=[0.6, 0.3, 0.1]),
            "situation": np.random.choice(["Open Play", "Set Piece", "Counter", "Penalty"], p=[0.7, 0.15, 0.1, 0.05]),
        })
    return pd.DataFrame(shots)


shots_home = gen_shot_data(n_shots_home, "Arsenal")
shots_away = gen_shot_data(n_shots_away, "Opponent")
all_shots = pd.concat([shots_home, shots_away], ignore_index=True)

# ── Row 1: xG Timeline + Shot Map ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='glass-card'><h3>📈 xG Timeline</h3>", unsafe_allow_html=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3],
                        vertical_spacing=0.05)

    home_shots_sorted = shots_home.sort_values("minute")
    away_shots_sorted = shots_away.sort_values("minute")

    fig.add_trace(go.Bar(
        x=home_shots_sorted["minute"], y=home_shots_sorted["xG"],
        name="Arsenal",
        marker_color=ARSENAL_RED,
        opacity=0.8,
        hovertemplate="Min %{x}<br>xG: %{y:.2f}<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=away_shots_sorted["minute"], y=away_shots_sorted["xG"],
        name="Opponent",
        marker_color=NEON_CYAN,
        opacity=0.6,
        hovertemplate="Min %{x}<br>xG: %{y:.2f}<extra></extra>",
    ), row=1, col=1)

    # Cumulative xG
    if not home_shots_sorted.empty:
        home_cum = home_shots_sorted["xG"].cumsum()
        fig.add_trace(go.Scatter(
            x=home_shots_sorted["minute"], y=home_cum,
            mode="lines", name="Arsenal (cum)",
            line=dict(color=ARSENAL_RED, width=2, dash="dot"),
        ), row=1, col=1)
    if not away_shots_sorted.empty:
        away_cum = away_shots_sorted["xG"].cumsum()
        fig.add_trace(go.Scatter(
            x=away_shots_sorted["minute"], y=away_cum,
            mode="lines", name="Opponent (cum)",
            line=dict(color=NEON_CYAN, width=2, dash="dot"),
        ), row=1, col=1)

    # Momentum bar
    if not home_shots_sorted.empty and not away_shots_sorted.empty:
        all_mins = np.arange(0, 96, 5)
        home_window = home_shots_sorted.set_index("minute").reindex(all_mins, method="ffill").fillna(0)
        away_window = away_shots_sorted.set_index("minute").reindex(all_mins, method="ffill").fillna(0)
        momentum = home_window["xG"].rolling(3, min_periods=1).mean() - away_window["xG"].rolling(3, min_periods=1).mean()

        momentum_colors = [ARSENAL_RED if v > 0 else (NEON_CYAN if v < 0 else "#4A5568") for v in momentum]
        fig.add_trace(go.Bar(
            x=all_mins, y=momentum,
            marker_color=momentum_colors,
            name="Momentum",
            hovertemplate="Min %{x}<br>Momentum: %{y:.2f}<extra></extra>",
        ), row=2, col=1)

    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=500,
        xaxis=dict(title="Minute", gridcolor=GRID_COLOR, range=[0, 96]),
        yaxis=dict(title="xG", gridcolor=GRID_COLOR),
        hovermode="x unified",
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'><h3>🎯 Shot Map</h3>", unsafe_allow_html=True)
    pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                  line_color=GRID_COLOR, linewidth=1.5, axis=False, label=False)
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)

    # Home shots
    for _, s in shots_home.iterrows():
        size = max(np.sqrt(s["xG"]) * 60, 30)
        color = ARSENAL_RED
        edge = "#FFD700" if s["goal"] else ARSENAL_RED
        pitch.scatter(s["x"], s["y"], s=size, ax=ax, color=color,
                      edgecolors=edge, linewidth=2, alpha=0.7, zorder=5)

    # Away shots
    for _, s in shots_away.iterrows():
        size = max(np.sqrt(s["xG"]) * 50, 25)
        pitch.scatter(s["x"], s["y"], s=size, ax=ax, color=NEON_CYAN,
                      edgecolors=NEON_CYAN, linewidth=1.5, alpha=0.5, zorder=4)

    # Goal indicators
    goals_home = shots_home[shots_home["goal"]]
    for _, s in goals_home.iterrows():
        pitch.scatter(s["x"], s["y"], s=120, ax=ax, color="none",
                      edgecolors="#FFD700", linewidth=3, alpha=0.8, zorder=6)
        ax.annotate("⚽", (s["x"], s["y"]), fontsize=14, ha="center", va="center")

    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 2: Shot Analysis ──
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("<div class='glass-card'><h3>🎯 Shot Outcome</h3>", unsafe_allow_html=True)
    outcomes = ["Goal", "Saved", "Blocked", "Off Target", "Hit Woodwork"]
    counts = np.random.multinomial(n_shots_home + n_shots_away, [0.12, 0.35, 0.25, 0.25, 0.03])
    fig = go.Figure(data=[go.Pie(
        labels=outcomes, values=counts,
        marker_colors=["#FFD700", ARSENAL_RED, "#4A5568", "#2D3748", NEON_CYAN],
        hole=0.5,
        textinfo="label+percent",
        textfont=dict(color="white", size=11),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='glass-card'><h3>🦶 Shot Body Part</h3>", unsafe_allow_html=True)
    body_parts = all_shots["body_part"].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=body_parts.index, values=body_parts.values,
        marker_colors=[ARSENAL_RED, NEON_CYAN, "#9C824A"],
        hole=0.5,
        textinfo="label+percent",
        textfont=dict(color="white", size=11),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col5:
    st.markdown("<div class='glass-card'><h3>📊 Shot Situation</h3>", unsafe_allow_html=True)
    situations = all_shots["situation"].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=situations.index, values=situations.values,
        marker_colors=[ARSENAL_RED, NEON_CYAN, "#00D4AA", "#FFB347"],
        hole=0.5,
        textinfo="label+percent",
        textfont=dict(color="white", size=11),
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: xG summary ──
col6, col7, col8 = st.columns(3)
total_xg_home = shots_home["xG"].sum()
total_xg_away = shots_away["xG"].sum()

with col6:
    st.markdown(
        f"<div class='glass-card' style='text-align:center;'>"
        f"<div style='font-size:1rem;color:{NEON_CYAN};text-transform:uppercase;letter-spacing:2px;'>Total xG</div>"
        f"<div style='display:flex;justify-content:center;gap:40px;margin-top:12px;'>"
        f"<div><span style='color:{ARSENAL_RED};font-size:2.5rem;font-family:IBM Plex Mono;font-weight:700;'>{total_xg_home:.2f}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Arsenal</span></div>"
        f"<div><span style='color:{NEON_CYAN};font-size:2.5rem;font-family:IBM Plex Mono;font-weight:700;'>{total_xg_away:.2f}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Opponent</span></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

with col7:
    st.markdown(
        f"<div class='glass-card' style='text-align:center;'>"
        f"<div style='font-size:1rem;color:{NEON_CYAN};text-transform:uppercase;letter-spacing:2px;'>Shots</div>"
        f"<div style='display:flex;justify-content:center;gap:40px;margin-top:12px;'>"
        f"<div><span style='color:{ARSENAL_RED};font-size:2.5rem;font-family:IBM Plex Mono;font-weight:700;'>{n_shots_home}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Arsenal</span></div>"
        f"<div><span style='color:{NEON_CYAN};font-size:2.5rem;font-family:IBM Plex Mono;font-weight:700;'>{n_shots_away}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Opponent</span></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

with col8:
    st.markdown(
        f"<div class='glass-card' style='text-align:center;'>"
        f"<div style='font-size:1rem;color:{NEON_CYAN};text-transform:uppercase;letter-spacing:2px;'>Big Chances (xG > 0.3)</div>"
        f"<div style='display:flex;justify-content:center;gap:40px;margin-top:12px;'>"
        f"<div><span style='color:{ARSENAL_RED};font-size:2.5rem;font-family:IBM Plex Mono;font-weight:700;'>{(shots_home['xG'] > 0.3).sum()}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Arsenal</span></div>"
        f"<div><span style='color:{NEON_CYAN};font-size:2.5rem;font-family:IBM Plex Mono;font-weight:700;'>{(shots_away['xG'] > 0.3).sum()}</span><br><span style='color:#8892B0;font-size:0.8rem;'>Opponent</span></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )
