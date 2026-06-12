"""
Recruitment Analysis — similar players, scatter plots, age curve,
market value, and recruitment scoring.
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

st.markdown("<h2>🔍 Recruitment Analysis</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8892B0;'>Scouting · Market value · Age curves · Similar player identification</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Synthetic recruitment data ──
np.random.seed(42)

TARGET_POSITIONS = {
    "Striker (CF)": {
        "players": [
            {"name": "Viktor Gyokeres", "age": 26, "club": "Sporting CP", "val": 65, "goals": 32, "xg": 28.5, "xa": 6.2, "assists": 8, "apps": 38, "mins": 3200, "country": "Sweden", "contract": 2028, "score": 92},
            {"name": "Victor Osimhen", "age": 26, "club": "Napoli", "val": 80, "goals": 28, "xg": 24.1, "xa": 4.8, "assists": 5, "apps": 34, "mins": 2900, "country": "Nigeria", "contract": 2026, "score": 91},
            {"name": "Benjamin Sesko", "age": 22, "club": "RB Leipzig", "val": 50, "goals": 18, "xg": 16.5, "xa": 3.5, "assists": 4, "apps": 36, "mins": 2500, "country": "Slovenia", "contract": 2029, "score": 85},
            {"name": "Jonathan David", "age": 25, "club": "Lille", "val": 45, "goals": 22, "xg": 20.2, "xa": 5.1, "assists": 6, "apps": 37, "mins": 3000, "country": "Canada", "contract": 2027, "score": 80},
            {"name": "Evan Ferguson", "age": 20, "club": "Brighton", "val": 35, "goals": 12, "xg": 10.8, "xa": 2.2, "assists": 3, "apps": 28, "mins": 1800, "country": "Ireland", "contract": 2029, "score": 76},
            {"name": "Santiago Gimenez", "age": 24, "club": "Feyenoord", "val": 40, "goals": 20, "xg": 18.5, "xa": 3.8, "assists": 5, "apps": 32, "mins": 2600, "country": "Mexico", "contract": 2027, "score": 78},
        ]
    },
    "Left Winger": {
        "players": [
            {"name": "Rafael Leao", "age": 25, "club": "AC Milan", "val": 75, "goals": 14, "xg": 12.5, "xa": 8.2, "assists": 10, "apps": 35, "mins": 2900, "country": "Portugal", "contract": 2028, "score": 88},
            {"name": "Kvaratskhelia", "age": 24, "club": "Napoli", "val": 65, "goals": 12, "xg": 10.8, "xa": 9.5, "assists": 11, "apps": 34, "mins": 2750, "country": "Georgia", "contract": 2027, "score": 86},
            {"name": "Nico Williams", "age": 22, "club": "Athletic Club", "val": 50, "goals": 8, "xg": 7.2, "xa": 11.5, "assists": 14, "apps": 36, "mins": 2800, "country": "Spain", "contract": 2027, "score": 82},
            {"name": "Kingsley Coman", "age": 29, "club": "Bayern", "val": 45, "goals": 9, "xg": 8.5, "xa": 6.8, "assists": 8, "apps": 30, "mins": 2200, "country": "France", "contract": 2027, "score": 75},
            {"name": "Johan Bakayoko", "age": 22, "club": "PSV", "val": 35, "goals": 10, "xg": 9.2, "xa": 7.5, "assists": 9, "apps": 34, "mins": 2400, "country": "Belgium", "contract": 2028, "score": 74},
        ]
    },
    "Central Midfielder": {
        "players": [
            {"name": "Bruno Guimaraes", "age": 27, "club": "Newcastle", "val": 70, "goals": 7, "xg": 5.8, "xa": 6.5, "assists": 7, "apps": 35, "mins": 3100, "country": "Brazil", "contract": 2028, "score": 87},
            {"name": "Frenkie de Jong", "age": 28, "club": "Barcelona", "val": 60, "goals": 4, "xg": 3.5, "xa": 5.2, "assists": 5, "apps": 28, "mins": 2400, "country": "Netherlands", "contract": 2026, "score": 82},
            {"name": "Douglas Luiz", "age": 26, "club": "Aston Villa", "val": 55, "goals": 9, "xg": 7.8, "xa": 7.2, "assists": 8, "apps": 36, "mins": 3100, "country": "Brazil", "contract": 2026, "score": 84},
            {"name": "Manuel Ugarte", "age": 24, "club": "PSG", "val": 45, "goals": 2, "xg": 1.8, "xa": 3.5, "assists": 4, "apps": 32, "mins": 2500, "country": "Uruguay", "contract": 2028, "score": 76},
            {"name": "Joao Neves", "age": 20, "club": "Benfica", "val": 55, "goals": 5, "xg": 4.2, "xa": 6.8, "assists": 7, "apps": 34, "mins": 2700, "country": "Portugal", "contract": 2028, "score": 79},
        ]
    },
    "Right Back": {
        "players": [
            {"name": "Jeremie Frimpong", "age": 24, "club": "Bayer Leverkusen", "val": 50, "goals": 8, "xg": 6.5, "xa": 8.2, "assists": 10, "apps": 36, "mins": 3000, "country": "Netherlands", "contract": 2028, "score": 84},
            {"name": "Joao Cancelo", "age": 30, "club": "Barcelona", "val": 35, "goals": 3, "xg": 2.5, "xa": 4.8, "assists": 5, "apps": 30, "mins": 2500, "country": "Portugal", "contract": 2027, "score": 74},
            {"name": "Reece James", "age": 25, "club": "Chelsea", "val": 40, "goals": 3, "xg": 2.2, "xa": 5.5, "assists": 6, "apps": 22, "mins": 1800, "country": "England", "contract": 2028, "score": 72},
            {"name": "Vanderson", "age": 23, "club": "Monaco", "val": 30, "goals": 2, "xg": 1.8, "xa": 4.2, "assists": 5, "apps": 32, "mins": 2600, "country": "Brazil", "contract": 2027, "score": 71},
        ]
    },
}

# ── Position selector ──
pos_options = list(TARGET_POSITIONS.keys())
col_sel, _ = st.columns([1, 2])

with col_sel:
    st.markdown("<div class='glass-card'><h3>🎯 Target Position</h3>", unsafe_allow_html=True)
    selected_pos = st.selectbox("", pos_options, index=0, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

pos_data = TARGET_POSITIONS[selected_pos]
recruits_df = pd.DataFrame(pos_data["players"])

# ── Row 1: KPI cards ──
cols = st.columns(5)
top3 = recruits_df.nlargest(3, "score")
kpi_data = [
    ("🥇", "Top Target", top3.iloc[0]["name"]),
    ("💰", "Avg Value", f"£{recruits_df['val'].mean():.0f}m"),
    ("📊", "Avg Score", f"{recruits_df['score'].mean():.0f}"),
    ("📈", "Best Value", recruits_df.loc[(recruits_df['val'] / recruits_df['score']).idxmin(), "name"]),
    ("🎯", "Top xG", recruits_df.nlargest(1, "xg").iloc[0]["name"]),
]
for i, (icon, label, val) in enumerate(kpi_data):
    with cols[i]:
        st.markdown(
            f"<div class='glass-card' style='text-align:center;padding:14px;'>"
            f"<div style='font-size:1.2rem;'>{icon}</div>"
            f"<div style='color:white;font-family:IBM Plex Mono;font-weight:700;font-size:0.95rem;'>{val}</div>"
            f"<div class='kpi-label'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Row 2: Scatter plots ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='glass-card'><h3>💵 Market Value vs Performance Score</h3>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recruits_df["val"], y=recruits_df["score"],
        mode="markers+text",
        text=recruits_df["name"],
        textposition="top center",
        textfont=dict(size=10, color="white"),
        marker=dict(
            size=recruits_df["xg"] * 2 + 15,
            color=recruits_df["age"],
            colorscale=[[0, NEON_CYAN], [0.5, GOLD], [1, ARSENAL_RED]],
            showscale=True,
            colorbar=dict(title="Age", tickfont=dict(color=TEXT_COLOR)),
            line=dict(color="white", width=1),
        ),
        hovertemplate="<b>%{text}</b><br>Value: £%{x}m<br>Score: %{y}<br>xG: %{marker.size:.1f}<br>Age: %{marker.color}<extra></extra>",
    ))
    # Add Arsenal reference zone (players with score > 80, value < 60)
    fig.add_shape(type="rect", x0=0, x1=60, y0=80, y1=100,
                  line=dict(dash="dash", color=ARSENAL_RED, width=2),
                  fillcolor="rgba(239,1,7,0.05)")
    fig.add_annotation(x=30, y=98, text="Arsenal<br>Target Zone", showarrow=False,
                       font=dict(size=10, color=ARSENAL_RED))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=450,
        xaxis=dict(title="Market Value (£m)", gridcolor=GRID_COLOR),
        yaxis=dict(title="Recruitment Score", gridcolor=GRID_COLOR),
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'><h3>📈 Age Curve — Productivity vs Age</h3>", unsafe_allow_html=True)

    # Add Arsenal current players for comparison
    arsenal_fwds = [
        {"name": "Saka", "age": 23, "xg": 15.2, "val": 120},
        {"name": "Havertz", "age": 25, "xg": 9.1, "val": 70},
        {"name": "Martinelli", "age": 23, "xg": 8.8, "val": 70},
        {"name": "Jesus", "age": 28, "xg": 11.5, "val": 55},
        {"name": "Trossard", "age": 30, "xg": 6.2, "val": 35},
        {"name": "Odegaard", "age": 26, "xg": 10.8, "val": 85},
    ]
    arsenal_df = pd.DataFrame(arsenal_fwds)

    fig = go.Figure()

    # Arsenal current players
    fig.add_trace(go.Scatter(
        x=arsenal_df["age"], y=arsenal_df["xg"],
        mode="markers+text",
        text=arsenal_df["name"],
        textposition="bottom center",
        textfont=dict(size=9, color="white"),
        marker=dict(
            size=arsenal_df["val"] * 0.15 + 10,
            color=ARSENAL_RED,
            symbol="circle",
            line=dict(color="white", width=1.5),
        ),
        name="Arsenal Current",
        hovertemplate="<b>%{text}</b><br>Age: %{x}<br>xG: %{y:.1f}<extra></extra>",
    ))

    # Target players
    fig.add_trace(go.Scatter(
        x=recruits_df["age"], y=recruits_df["xg"],
        mode="markers+text",
        text=recruits_df["name"],
        textposition="top center",
        textfont=dict(size=9, color="white"),
        marker=dict(
            size=recruits_df["val"] * 0.15 + 10,
            color=NEON_CYAN,
            symbol="diamond",
            line=dict(color="white", width=1.5),
        ),
        name="Targets",
        hovertemplate="<b>%{text}</b><br>Age: %{x}<br>xG: %{y:.1f}<br>£%{marker.size:.0f}m<extra></extra>",
    ))

    # Peak age shading
    fig.add_vrect(x0=22, x1=27, fillcolor="rgba(0,245,255,0.06)", layer="below",
                  line_width=0, annotation_text="Peak", annotation_position="top left")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=450,
        xaxis=dict(title="Age", gridcolor=GRID_COLOR, range=[18, 34]),
        yaxis=dict(title="xG", gridcolor=GRID_COLOR),
        hovermode="closest",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Row 3: Detailed comparison ──
col3, col4 = st.columns(2)

with col3:
    st.markdown("<div class='glass-card'><h3>📊 Player Comparison Matrix</h3>", unsafe_allow_html=True)

    fig = go.Figure()
    for _, r in recruits_df.iterrows():
        rad = min(r["xg"] / r["apps"] * 10, 0.8) if r["apps"] > 0 else 0
        fig.add_trace(go.Scatterpolar(
            r=[r["score"], r["xg"], r["xa"], r["val"] / 10, r["goals"] / r["apps"] * 10 if r["apps"] > 0 else 0,
               r["age"] / 3, rad],
            theta=["Score", "xG", "xA", "Value/10", "Gls/90", "Age/3", "xG/Shot"],
            fill="toself",
            name=r["name"],
            opacity=0.6,
            line=dict(width=1),
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=500,
        polar=dict(
            bgcolor="rgba(13,17,23,0.4)",
            angularaxis=dict(color=TEXT_COLOR, gridcolor=GRID_COLOR),
            radialaxis=dict(color=TEXT_COLOR, gridcolor=GRID_COLOR, showticklabels=False),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COLOR, size=9)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='glass-card'><h3>📋 Scouting Report</h3>", unsafe_allow_html=True)

    selected_target = st.selectbox("Select target for detailed report", recruits_df["name"].tolist())
    target = recruits_df[recruits_df["name"] == selected_target].iloc[0]

    st.markdown(
        f"<div style='padding:12px;background:rgba(239,1,7,0.06);border-radius:12px;border:1px solid rgba(239,1,7,0.2);'>"
        f"<h4 style='color:white;margin-bottom:8px;'>{target['name']}</h4>"
        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>"
        f"<div><span style='color:{TEXT_COLOR};'>Club</span><br><span style='color:white;font-weight:600;'>{target['club']}</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>Age</span><br><span style='color:white;font-weight:600;'>{target['age']}</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>Market Value</span><br><span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>£{target['val']}m</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>Country</span><br><span style='color:white;font-weight:600;'>{target['country']}</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>Contract Until</span><br><span style='color:white;font-weight:600;'>{target['contract']}</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>Recruitment Score</span><br><span style='color:{ARSENAL_RED};font-weight:700;font-family:IBM Plex Mono;font-size:1.3rem;'>{target['score']}/100</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>xG</span><br><span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>{target['xg']:.1f}</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>xA</span><br><span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>{target['xa']:.1f}</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>Goals</span><br><span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>{target['goals']}</span></div>"
        f"<div><span style='color:{TEXT_COLOR};'>Assists</span><br><span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>{target['assists']}</span></div>"
        f"</div>"
        f"<div style='margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);'>"
        f"<span style='color:{TEXT_COLOR};'>Minutes per Goal: </span>"
        f"<span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>{target['mins'] // target['goals'] if target['goals'] > 0 else 'N/A'} min</span>"
        f"<br><span style='color:{TEXT_COLOR};'>xG per 90: </span>"
        f"<span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>{target['xg'] / target['mins'] * 90:.2f}</span>"
        f"<br><span style='color:{TEXT_COLOR};'>Value per xG: </span>"
        f"<span style='color:white;font-weight:600;font-family:IBM Plex Mono;'>£{target['val'] / target['xg']:.1f}m</span>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Similarity comparison
    st.markdown("<h4 style='margin-top:16px;color:#8892B0;'>🔗 Similarity to Arsenal Current Players</h4>", unsafe_allow_html=True)

    similarity_data = []
    for _, ars in arsenal_df.iterrows():
        age_sim = max(0, 100 - abs(target["age"] - ars["age"]) * 10)
        xg_sim = max(0, 100 - abs(target["xg"] / target["mins"] * 90 - ars["xg"]) * 20) if target["mins"] > 0 else 50
        overall = round((age_sim + xg_sim) / 2, 0)
        similarity_data.append({"Arsenal Player": ars["name"], "Similarity %": overall})

    sim_df = pd.DataFrame(similarity_data).sort_values("Similarity %", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=sim_df["Arsenal Player"], x=sim_df["Similarity %"],
        orientation="h",
        marker_color=np.where(sim_df["Similarity %"] >= sim_df["Similarity %"].max(), ARSENAL_RED, NEON_CYAN),
        text=sim_df["Similarity %"].apply(lambda x: f"{x:.0f}%"),
        textposition="outside",
        hovertemplate="%{y}: %{x:.0f}% similar<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_COLOR), height=280,
        xaxis=dict(title="Similarity %", gridcolor=GRID_COLOR, range=[0, 115]),
        yaxis=dict(gridcolor=GRID_COLOR),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
