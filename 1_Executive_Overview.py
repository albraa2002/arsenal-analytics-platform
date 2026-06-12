"""
Executive Overview — season KPIs, trend charts, and match timeline.
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


def load():
    files = {
        "matches": "fact_matches.csv",
        "players": "dim_players.csv",
        "player_stats": "fact_player_match_stats.csv",
    }
    data = {}
    for key, fname in files.items():
        p = DATA_DIR / fname
        data[key] = pd.read_csv(p) if p.exists() else pd.DataFrame()
    return data


DATA = load()
df = DATA["matches"]


# ── Helper ──
def kpi_card(icon, label, value, suffix=""):
    return f"""
    <div class='glass-card animate-in' style='text-align:center;padding:20px;'>
        <div style='font-size:2rem;margin-bottom:6px;'>{icon}</div>
        <div class='kpi-number'>{value}{suffix}</div>
        <div class='kpi-label'>{label}</div>
    </div>
    """


st.markdown("<h2>📊 Executive Overview</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#8892B0;'>Season 2025/26 · Aggregate Performance Metrics</p>", unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("No match data available. Run the data pipeline first.")
    st.stop()

# ── Compute KPIs ──
total_matches = len(df)
home_wins = len(df[df["home_score"].fillna(0) > df["away_score"].fillna(0)])
away_wins = len(df[df["away_score"].fillna(0) > df["home_score"].fillna(0)])
draws = len(df[df["home_score"].fillna(0) == df["away_score"].fillna(0)])
total_wins = home_wins + away_wins
win_pct = round(total_wins / total_matches * 100, 1) if total_matches else 0
losses = total_matches - total_wins - draws

total_goals_for = int(df["home_score"].fillna(0).sum() + df["away_score"].fillna(0).sum())
total_goals_against = int(df["away_score"].fillna(0).sum() + df["home_score"].fillna(0).sum())
goal_diff = total_goals_for - total_goals_against

total_xg = round(df["home_xG"].fillna(0).sum(), 1) if "home_xG" in df.columns else 0
total_xga = round(df["away_xGA"].fillna(0).sum(), 1) if "away_xGA" in df.columns else 0

poss = df["home_possession_pct"].dropna()
avg_poss = round(poss.mean(), 1) if not poss.empty else 0

clean_sheets = int((df["home_score"] == 0).sum() + (df["away_score"] == 0).sum()) if "home_score" in df.columns else 0

ppda = df["home_ppda"].dropna()
avg_ppda = round(ppda.mean(), 1) if not ppda.empty else 0

points = total_wins * 3 + draws
xpts = round(total_xg - total_xga + points, 1) if total_xg and total_xga else 0

# ── Row 1: Core KPIs ──
st.markdown("<h3 style='color:#00F5FF;font-size:0.9rem;letter-spacing:2px;text-transform:uppercase;'>🏆 Season Summary</h3>", unsafe_allow_html=True)
cols = st.columns(6)
kpi_data = [
    ("🏆", "Points", points),
    ("🎯", "xPTS", xpts),
    ("⚽", "Goals For", total_goals_for),
    ("🛡️", "Goals Against", total_goals_against),
    ("📊", "Goal Diff", f"+{goal_diff}" if goal_diff > 0 else str(goal_diff)),
    ("✅", "Wins", total_wins),
]
for i, (icon, label, val) in enumerate(kpi_data):
    with cols[i]:
        st.markdown(kpi_card(icon, label, val), unsafe_allow_html=True)

# ── Row 2: Advanced KPIs ──
cols2 = st.columns(6)
kpi2 = [
    ("🎯", "xG", total_xg),
    ("🛡️", "xGA", total_xga),
    ("📏", "Possession %", f"{avg_poss}%"),
    ("📈", "Win %", f"{win_pct}%"),
    ("🧤", "Clean Sheets", clean_sheets),
    ("🔄", "PPDA", avg_ppda),
]
for i, (icon, label, val) in enumerate(kpi2):
    with cols2[i]:
        st.markdown(kpi_card(icon, label, val), unsafe_allow_html=True)

st.markdown("---")

# ── Trend Charts ──
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='glass-card'><h3>📈 Form Trend (Points per Match)</h3>", unsafe_allow_html=True)
    if "match_id" in df.columns:
        df_plot = df.copy()
        if "home_score" in df_plot.columns and "away_score" in df_plot.columns:
            df_plot["match_no"] = range(1, len(df_plot) + 1)
            df_plot["result_points"] = np.where(
                df_plot["home_score"] > df_plot["away_score"], 3,
                np.where(df_plot["home_score"] == df_plot["away_score"], 1, 0),
            )
            df_plot["cumulative_points"] = df_plot["result_points"].cumsum()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_plot["match_no"], y=df_plot["cumulative_points"],
                mode="lines+markers",
                name="Points",
                line=dict(color="#EF0107", width=3),
                marker=dict(size=8, color="#EF0107", line=dict(color="white", width=1)),
                fill="tozeroy", fillcolor="rgba(239,1,7,0.08)",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8892B0"), height=350,
                xaxis=dict(title="Match", gridcolor="#1A2332"),
                yaxis=dict(title="Points", gridcolor="#1A2332"),
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-card'><h3>⚽ Goals & xG Trend</h3>", unsafe_allow_html=True)
    if all(c in df.columns for c in ["home_score", "home_xG"]):
        df_plot = df.copy()
        df_plot["match_no"] = range(1, len(df_plot) + 1)
        df_plot["goals_scored"] = df_plot["home_score"].fillna(0)
        df_plot["cum_goals"] = df_plot["goals_scored"].cumsum()
        df_plot["cum_xG"] = df_plot["home_xG"].fillna(0).cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_plot["match_no"], y=df_plot["cum_goals"],
            mode="lines+markers", name="Goals",
            line=dict(color="#EF0107", width=3),
            marker=dict(size=8, color="#EF0107"),
        ))
        fig.add_trace(go.Scatter(
            x=df_plot["match_no"], y=df_plot["cum_xG"],
            mode="lines+markers", name="xG",
            line=dict(color="#00F5FF", width=3, dash="dot"),
            marker=dict(size=8, color="#00F5FF"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892B0"), height=350,
            xaxis=dict(title="Match", gridcolor="#1A2332"),
            yaxis=dict(title="Cumulative", gridcolor="#1A2332"),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ── Match Result Timeline ──
col3, col4 = st.columns([2, 1])

with col3:
    st.markdown("<div class='glass-card'><h3>📅 Match Result Timeline</h3>", unsafe_allow_html=True)
    if all(c in df.columns for c in ["home_score", "away_score"]):
        df_res = df.copy()
        df_res["match_no"] = range(1, len(df_res) + 1)
        df_res["result"] = df_res.apply(
            lambda r: "W" if r["home_score"] > r["away_score"]
            else ("D" if r["home_score"] == r["away_score"] else "L"),
            axis=1,
        )
        colors = {"W": "#00D4AA", "D": "#FFB347", "L": "#FF4757"}
        df_res["color"] = df_res["result"].map(colors)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_res["match_no"], y=df_res["home_score"].fillna(0),
            name="Goals For", marker_color="#EF0107",
            hovertemplate="Match %{x}<br>GF: %{y}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            x=df_res["match_no"], y=df_res["away_score"].fillna(0),
            name="Goals Against", marker_color="#4A5568",
            hovertemplate="Match %{x}<br>GA: %{y}<extra></extra>",
        ))
        for _, r in df_res.iterrows():
            fig.add_annotation(
                x=r["match_no"], y=max(r["home_score"], r["away_score"]) + 0.3,
                text=f"<b>{r['result']}</b>",
                showarrow=False, font=dict(color=r["color"], size=12),
            )

        fig.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892B0"), height=400,
            xaxis=dict(title="Match", gridcolor="#1A2332", dtick=1),
            yaxis=dict(title="Goals", gridcolor="#1A2332"),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='glass-card'><h3>📊 Result Split</h3>", unsafe_allow_html=True)
    if total_wins or draws or losses:
        fig = go.Figure(data=[go.Pie(
            labels=["Wins", "Draws", "Losses"],
            values=[total_wins, draws, losses],
            marker_colors=["#00D4AA", "#FFB347", "#FF4757"],
            hole=0.6,
            textinfo="label+percent",
            textfont=dict(color="white", size=14),
        )])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892B0"),
            height=400,
            showlegend=False,
            annotations=[dict(
                text=f"{total_wins}W<br>{draws}D<br>{losses}L",
                x=0.5, y=0.5, font=dict(size=18, color="white"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Performance Breakdown ──
st.markdown("---")
col5, col6, col7 = st.columns(3)

with col5:
    st.markdown("<div class='glass-card'><h3>⚽ Goal Analysis</h3>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=total_goals_for,
        delta={"reference": total_goals_against, "position": "top"},
        title={"text": "Goals For vs Against"},
        gauge={"axis": {"range": [None, max(total_goals_for, total_goals_against) + 5]},
               "bar": {"color": "#EF0107"},
               "bgcolor": "rgba(0,0,0,0)",
               "borderwidth": 0,
               "steps": [{"range": [0, total_goals_against], "color": "rgba(239,1,7,0.15)"}],
               "threshold": {"line": {"color": "#00F5FF", "width": 4}, "thickness": 0.75, "value": total_goals_against}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#8892B0"), height=250,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col6:
    st.markdown("<div class='glass-card'><h3>🎯 xG vs Actual</h3>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["xG", "Goals"],
        y=[total_xg, total_goals_for],
        marker_color=["#00F5FF", "#EF0107"],
        text=[f"{total_xg:.1f}", str(total_goals_for)],
        textposition="outside",
        textfont=dict(size=18, color="white"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8892B0"), height=250,
        yaxis=dict(gridcolor="#1A2332"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col7:
    st.markdown("<div class='glass-card'><h3>🛡️ Defensive Summary</h3>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number+gauge+delta",
        value=clean_sheets,
        delta={"reference": total_matches - clean_sheets, "position": "top"},
        title={"text": "Clean Sheets"},
        gauge={"axis": {"range": [None, total_matches]},
               "bar": {"color": "#00D4AA"},
               "bgcolor": "rgba(0,0,0,0)",
               "borderwidth": 0,
               "steps": [{"range": [0, total_matches // 2], "color": "rgba(0,212,170,0.1)"}],
               "threshold": {"line": {"color": "#EF0107", "width": 4}, "thickness": 0.75, "value": total_matches}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#8892B0"), height=250,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
