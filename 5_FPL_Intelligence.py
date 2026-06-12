"""
FPL Intelligence — player prices, ownership, predicted points,
captain picks, form vs fixture difficulty.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data" / "final"

DARK_BG = "#060B18"
GRID_COLOR = "#1A2332"
ARSENAL_RED = "#EF0107"
NEON_CYAN = "#00F5FF"
TEXT_COLOR = "#8892B0"
GOLD = "#9C824A"

st.markdown("<h2>💰 FPL Intelligence</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8892B0;'>Fantasy Premier League · Player prices · Ownership · Predicted points · Captain picks</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Generate synthetic FPL data ──
np.random.seed(42)

fpl_squad = [
    {"name": "Saka", "pos": "MID", "price": 10.5, "owned": 42.3, "total_pts": 198, "ppg": 6.2,
     "form": 7.4, "xg": 15.2, "xa": 8.1, "ict": 284.5, "bonus": 18},
    {"name": "Odegaard", "pos": "MID", "price": 8.6, "owned": 28.7, "total_pts": 172, "ppg": 5.6,
     "form": 6.1, "xg": 10.8, "xa": 9.2, "ict": 256.3, "bonus": 14},
    {"name": "Rice", "pos": "MID", "price": 6.5, "owned": 18.2, "total_pts": 145, "ppg": 4.8,
     "form": 5.2, "xg": 6.4, "xa": 4.5, "ict": 212.8, "bonus": 10},
    {"name": "Havertz", "pos": "MID", "price": 7.8, "owned": 15.6, "total_pts": 138, "ppg": 4.6,
     "form": 5.8, "xg": 9.1, "xa": 5.3, "ict": 198.4, "bonus": 8},
    {"name": "Jesus", "pos": "FWD", "price": 8.0, "owned": 12.4, "total_pts": 112, "ppg": 5.1,
     "form": 4.8, "xg": 11.5, "xa": 4.2, "ict": 175.6, "bonus": 6},
    {"name": "Martinelli", "pos": "MID", "price": 7.2, "owned": 14.8, "total_pts": 128, "ppg": 4.3,
     "form": 5.5, "xg": 8.8, "xa": 4.9, "ict": 185.2, "bonus": 7},
    {"name": "Trossard", "pos": "MID", "price": 6.8, "owned": 8.5, "total_pts": 105, "ppg": 3.8,
     "form": 4.2, "xg": 6.2, "xa": 3.8, "ict": 152.3, "bonus": 5},
    {"name": "White", "pos": "DEF", "price": 5.5, "owned": 22.1, "total_pts": 118, "ppg": 3.6,
     "form": 4.5, "xg": 2.1, "xa": 3.2, "ict": 168.7, "bonus": 12},
    {"name": "Saliba", "pos": "DEF", "price": 5.3, "owned": 19.5, "total_pts": 108, "ppg": 3.3,
     "form": 3.8, "xg": 1.8, "xa": 1.5, "ict": 145.6, "bonus": 9},
    {"name": "Gabriel", "pos": "DEF", "price": 5.1, "owned": 16.8, "total_pts": 98, "ppg": 3.1,
     "form": 4.2, "xg": 3.5, "xa": 1.2, "ict": 138.4, "bonus": 8},
    {"name": "Raya", "pos": "GK", "price": 5.2, "owned": 25.6, "total_pts": 132, "ppg": 4.0,
     "form": 5.0, "xg": 0, "xa": 0.8, "ict": 122.5, "bonus": 15},
    {"name": "Zinchenko", "pos": "DEF", "price": 5.0, "owned": 10.2, "total_pts": 78, "ppg": 2.8,
     "form": 3.5, "xg": 1.2, "xa": 2.8, "ict": 112.3, "bonus": 4},
    {"name": "Partey", "pos": "MID", "price": 5.4, "owned": 6.8, "total_pts": 72, "ppg": 2.9,
     "form": 3.2, "xg": 1.8, "xa": 2.1, "ict": 98.5, "bonus": 3},
    {"name": "Nwaneri", "pos": "MID", "price": 4.5, "owned": 3.2, "total_pts": 42, "ppg": 2.8,
     "form": 4.8, "xg": 2.5, "xa": 1.8, "ict": 65.4, "bonus": 2},
]

df = pd.DataFrame(fpl_squad)

# ── Row 1: KPI cards ──
total_value = df["price"].sum()
total_points = df["total_pts"].sum()
avg_ppg = round(df["ppg"].mean(), 1)
most_owned = df.loc[df["owned"].idxmax(), "name"]
best_value = df.sort_values("total_pts", ascending=False).iloc[0]

cols = st.columns(5)
kpis = [
    ("💰", "Total Value", f"£{total_value:.1f}m"),
    ("📊", "Total Points", str(total_points)),
    ("📈", "Avg PPG", str(avg_ppg)),
    ("👥", "Most Owned", f"{most_owned} ({df['owned'].max():.1f}%)"),
    ("🏆", "Top Scorer", f"{best_value['name']} ({best_value['total_pts']}pts)"),
]
for i, (icon, label, val) in enumerate(kpis):
    with cols[i]:
        st.markdown(
            f"<div class='glass-card' style='text-align:center;padding:16px;'>"
            f"<div style='font-size:1.5rem;'>{icon}</div>"
            f"<div class='kpi-number' style='font-size:1.5rem;'>{val}</div>"
            f"<div class='kpi-label'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Row 2: Value chart + Ownership ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='glass-card'><h3>💵 Price vs Points (Value Analysis)</h3>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["price"], y=df["total_pts"],
        mode="markers+text",
        text=df["name"],
        textposition="top center",
        textfont=dict(size=10, color="white"),
        marker=dict(
            size=np.sqrt(df["owned"]) * 5 + 10,
            color=df["ppg"],
            colorscale=[[0, "#FF4757"], [0.5, "#FFB347"], [1, "#00D4AA"]],
            showscale=True,
            colorbar=dict(title="PPG", tickfont=dict(color=TEXT_COLOR)),
            line=dict(color="white", width=1),
        ),
        hovertemplate="<b>%{text}</b><br>Price: £%{x:.1f}m<br>Points: %{y}<br>Owned: %{marker.size:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=450,
        xaxis=dict(title="Price (£m)", gridcolor=GRID_COLOR),
        yaxis=dict(title="Total Points", gridcolor=GRID_COLOR),
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'><h3>👥 Ownership Distribution</h3>", unsafe_allow_html=True)
    df_sorted = df.sort_values("owned", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_sorted["name"], x=df_sorted["owned"],
        orientation="h",
        marker_color=ARSENAL_RED,
        marker_line=dict(color=NEON_CYAN, width=1),
        text=df_sorted["owned"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        textfont=dict(color=TEXT_COLOR, size=11),
        hovertemplate="%{y}: %{x:.1f}% owned<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=450,
        xaxis=dict(title="Ownership %", gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: Predicted Points + Form vs Fixture ──
col3, col4 = st.columns(2)

with col3:
    st.markdown("<div class='glass-card'><h3>🔮 Predicted Points (Next 3 GW)</h3>", unsafe_allow_html=True)
    np.random.seed(123)

    prediction_data = []
    for _, row in df.iterrows():
        base = row["ppg"]
        for gw in range(1, 4):
            noise = np.random.normal(0, 1.5)
            pred = max(0, base + noise + (gw * 0.2))
            prediction_data.append({
                "name": row["name"],
                "gw": f"GW{gw}",
                "predicted_pts": round(pred, 1),
            })

    pred_df = pd.DataFrame(prediction_data)
    pivot = pred_df.pivot(index="name", columns="gw", values="predicted_pts")
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=True)

    fig = go.Figure()
    for gw in ["GW1", "GW2", "GW3"]:
        fig.add_trace(go.Bar(
            y=pivot.index, x=pivot[gw],
            orientation="h", name=gw,
            marker_color={"GW1": ARSENAL_RED, "GW2": NEON_CYAN, "GW3": GOLD}[gw],
            marker_line=dict(color="rgba(255,255,255,0.2)", width=0.5),
        ))
    fig.add_trace(go.Scatter(
        y=pivot.index, x=pivot["total"],
        mode="markers",
        name="Total",
        marker=dict(color="white", size=10, symbol="diamond"),
    ))

    fig.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=500,
        xaxis=dict(title="Predicted Points", gridcolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR),
        hovermode="y unified",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='glass-card'><h3>📊 Form vs Fixture Difficulty</h3>", unsafe_allow_html=True)

    fixture_difficulty = {
        "GW1": "MCI (H)", "GW2": "TOT (A)", "GW3": "LEI (H)",
        "GW4": "LIV (H)", "GW5": "MUN (A)", "GW6": "CHE (H)",
    }

    # Synthetic form and difficulty
    difficulty_map = {"LEI (H)": 2, "CHE (H)": 4, "TOT (A)": 4, "MCI (H)": 5, "LIV (H)": 4, "MUN (A)": 4}
    top_players = df.nlargest(6, "form")[["name", "form", "ppg"]].copy()

    form_data = []
    for _, row in top_players.iterrows():
        for gw, opp in fixture_difficulty.items():
            diff = difficulty_map.get(opp, 3)
            expected = round(row["ppg"] * (1 - (diff - 2) * 0.08) + np.random.normal(0, 1), 1)
            form_data.append({
                "Player": row["name"],
                "GW": gw,
                "Opponent": opp,
                "Difficulty": diff,
                "Expected Pts": max(0, expected),
            })

    form_df = pd.DataFrame(form_data)

    fig = go.Figure()
    for player in top_players["name"].values[:4]:
        pdata = form_df[form_df["Player"] == player]
        fig.add_trace(go.Scatter(
            x=pdata["GW"], y=pdata["Expected Pts"],
            mode="lines+markers+text",
            name=player,
            text=pdata["Expected Pts"].apply(lambda x: f"{x:.1f}"),
            textposition="top center",
            textfont=dict(size=10, color="white"),
            line=dict(width=2.5),
            marker=dict(size=12),
            hovertemplate="%{x}<br>%{y:.1f} pts vs %{customdata}<extra></extra>",
            customdata=pdata["Opponent"],
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=500,
        xaxis=dict(title="Gameweek", gridcolor=GRID_COLOR),
        yaxis=dict(title="Expected Points", gridcolor=GRID_COLOR),
        hovermode="x unified",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 4: Captain Picks ──
st.markdown("<div class='glass-card'><h3>👑 Captaincy Analysis — Next Gameweek</h3>", unsafe_allow_html=True)

captain_candidates = df.nlargest(8, "form")[["name", "pos", "form", "ppg", "total_pts", "ict", "bonus"]].copy()
captain_candidates["captaincy_score"] = round(
    captain_candidates["form"] * 0.4 + captain_candidates["ppg"] * 0.3 +
    captain_candidates["bonus"] * 0.15 + captain_candidates["total_pts"] / 100 * 0.15, 1
)
captain_candidates = captain_candidates.sort_values("captaincy_score", ascending=True)

fig = go.Figure()
colors = [ARSENAL_RED if i >= len(captain_candidates) - 3 else NEON_CYAN
          for i in range(len(captain_candidates))]
fig.add_trace(go.Bar(
    y=captain_candidates["name"], x=captain_candidates["captaincy_score"],
    orientation="h",
    marker_color=colors,
    marker_line=dict(color="white", width=1),
    text=captain_candidates["captaincy_score"],
    textposition="outside",
    textfont=dict(color="white", size=13, family="IBM Plex Mono"),
    hovertemplate="<b>%{y}</b><br>Score: %{x}<br>Form: %{customdata[0]}<br>PPG: %{customdata[1]}<extra></extra>",
    customdata=captain_candidates[["form", "ppg"]],
))

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_COLOR), height=400,
    xaxis=dict(title="Captaincy Score", gridcolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
