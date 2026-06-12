"""
Arsenal FC 2025/26 — Interactive Football Analytics Dashboard
Streamlit multi-page app with glassmorphism dark theme.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Path setup ──
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data" / "final"
DB_DIR = ROOT / "database"

st.set_page_config(
    page_title="Arsenal FC · Analytics 25/26",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load custom CSS ──
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ── Data loading (cached) ──
@st.cache_data(show_spinner="Loading Arsenal data...")
def load_data() -> dict:
    files = {
        "players": "dim_players.csv",
        "matches": "fact_matches.csv",
        "player_stats": "fact_player_match_stats.csv",
        "shots": "fact_shots.csv",
        "fpl": "fact_fpl_gameweeks.csv",
    }
    data = {}
    for key, fname in files.items():
        path = DATA_DIR / fname
        if path.exists():
            data[key] = pd.read_csv(path)
        else:
            data[key] = pd.DataFrame()
    return data


DATA = load_data()

# ── Sidebar ──
with st.sidebar:
    st.markdown(
        "<h1 style='text-align:center;font-size:2rem;margin-bottom:4px;'>🔴</h1>"
        "<h2 style='text-align:center;font-size:1.2rem;margin-bottom:0;'>ARSENAL FC</h2>"
        "<p style='text-align:center;color:#8892B0;font-size:0.8rem;letter-spacing:2px;'>2025/26 · ANALYTICS</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    season = st.selectbox("Season", ["2025-2026"], index=0)
    if not DATA["matches"].empty and "competition_name" in DATA["matches"].columns:
        comps = ["All"] + sorted(DATA["matches"]["competition_name"].dropna().unique().tolist())
        competition = st.selectbox("Competition", comps, index=0)
    else:
        competition = "All"

    if not DATA["players"].empty and "position" in DATA["players"].columns:
        positions = ["All"] + sorted(DATA["players"]["position"].dropna().unique().tolist())
        pos_filter = st.selectbox("Position", positions, index=0)
    else:
        pos_filter = "All"

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#4A5568;font-size:0.7rem;'>"
        "Built with Streamlit · mplsoccer · Plotly<br>"
        "Data: FBref · Understat · FPL · StatsBomb · Fotmob · Transfermarkt"
        "</p>",
        unsafe_allow_html=True,
    )

# ── Header ──
st.markdown(
    "<div class='dashboard-header'>"
    "<div class='title-area'>"
    "<h1>Arsenal FC · Intelligence Platform</h1>"
    "<p>Season 2025/26 · Real-time Analytics & Tactical Insights</p>"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Quick KPIs row ──
if not DATA["matches"].empty:
    cols = st.columns(6)
    df = DATA["matches"]

    home_wins = len(df[df["home_score"].fillna(0) > df["away_score"].fillna(0)])
    away_wins = len(df[df["away_score"].fillna(0) > df["home_score"].fillna(0)])
    total_wins = home_wins + away_wins
    total_matches = len(df)
    win_pct = round(total_wins / total_matches * 100, 1) if total_matches else 0

    total_goals = int(df["home_score"].fillna(0).sum() + df["away_score"].fillna(0).sum())
    total_xg = round(df["home_xG"].fillna(0).sum(), 1) if "home_xG" in df.columns else 0
    total_xga = round(df["away_xGA"].fillna(0).sum(), 1) if "away_xGA" in df.columns else 0

    kpis = [
        ("🏆", "WINS", total_wins),
        ("📊", "WIN %", f"{win_pct}%"),
        ("⚽", "GOALS", total_goals),
        ("🎯", "xG", total_xg),
        ("🛡️", "xGA", total_xga),
        ("📈", "MATCHES", total_matches),
    ]
    for i, (icon, label, value) in enumerate(kpis):
        with cols[i]:
            st.markdown(
                f"<div class='glass-card animate-in' style='text-align:center;'>"
                f"<div style='font-size:1.8rem;margin-bottom:4px;'>{icon}</div>"
                f"<div class='kpi-number'>{value}</div>"
                f"<div class='kpi-label'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

# ── Render current page ──
# Streamlit auto-manages pages from the pages/ directory.
# This file serves as the entry point and home page.
st.markdown("---")
st.markdown(
    "<div style='text-align:center;padding:40px 0;'>"
    "<h2 style='color:#8892B0;font-weight:400;'>Select a page from the sidebar navigation</h2>"
    "<p style='color:#4A5568;'>Executive Overview · Tactical Analysis · Match Analysis · "
    "Player Analysis · FPL Intelligence · Recruitment Analysis</p>"
    "</div>",
    unsafe_allow_html=True,
)
