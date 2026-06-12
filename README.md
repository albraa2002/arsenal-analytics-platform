<<<<<<< HEAD
# Arsenal FC — Football Analytics Platform 2025/26

Production-grade, end-to-end football intelligence system for Arsenal FC's 2025/2026 season. Built for data engineers, analysts, and Power BI architects.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   DATA EXTRACTION                       │
│  FBref · Understat · FPL API · StatsBomb · Fotmob · TM │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   DATA CLEANING                         │
│  Column norm · Missing values · Outliers · Duplicates  │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 ENTITY RESOLUTION                       │
│        rapidfuzz · aliases · cross-source matching      │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 DATA WAREHOUSE (Star Schema)             │
│   dim_* · fact_matches · fact_player_stats · fact_*    │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│               FEATURE ENGINEERING                       │
│  PPDA · Field Tilt · xG/90 · Progressive · Tactical    │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              MACHINE LEARNING                           │
│  XGBoost · Random Forest · Logistic · Injury · FPL     │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              VISUALIZATION                              │
│  mplsoccer · Plotly · Heatmaps · Pass/Shot Maps         │
└──────────────────────┬──────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│            POWER BI EXPORT                              │
│  CSV · SQLite · Data Dictionary · Schema Docs           │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
football_analytics_project/
├── data/                    # Data lake (raw → processed → features → final)
├── scripts/
│   ├── extraction/          # 6 source-specific extractors
│   ├── preprocessing/       # Cleaning & normalization
│   ├── feature_engineering/ # Team, player & tactical metrics
│   ├── integration/         # Entity resolution + Power BI export
│   ├── modeling/            # ML models (match, player, injury, FPL)
│   └── visualization/       # mplsoccer & Plotly dashboards
├── database/                # Star schema definitions & setup
├── config/                  # Central configuration
├── notebooks/               # Jupyter analysis notebooks
├── dashboards/              # Power BI (.pbip) templates
├── outputs/                 # Plots, reports, trained models
├── docs/                    # Data dictionary & documentation
├── pipeline.py              # End-to-end orchestrator
└── requirements.txt
```

## Data Sources

| Source | Type | Data |
|--------|------|------|
| FBref | Scraping | Standard stats, shooting, passing, possession, defense, goalkeeping |
| Understat | Scraping (JSON) | xG, xGA, xPTS, shot maps, player shooting |
| FPL API | REST API | Player prices, ownership, ICT, bonus, gameweek history |
| StatsBomb | GitHub Open Data | Event data, passes, carries, pressures, freeze frames |
| Fotmob | Internal API | League tables, team matches, squad info |
| Transfermarkt | Scraping | Squad values, injuries, transfers, contracts |

## Quick Start

```bash
# Clone / navigate to project
cd football_analytics_project

# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python pipeline.py

# Run a specific phase
python pipeline.py --phase 1   # Extraction only
python pipeline.py --phase 4   # Database setup only
```

## Power BI Setup

1. Run `python pipeline.py` to generate all CSVs and SQLite DB
2. Open Power BI Desktop
3. Get Data → CSV / SQLite → navigate to `data/final/` or `database/`
4. Apply star schema relationships from `docs/relationships.md`
5. Apply theme from `dashboards/arsenal_theme.json`

## Dashboard Pages

| Page | Content |
|------|---------|
| Executive Overview | Season KPIs, league position, form, xG trends |
| Tactical Analysis | Average positions, passing networks, PPDA, field tilt |
| Match Analysis | xG timeline, shot maps, pass maps, heatmaps |
| Player Analysis | Radars, percentiles, per-90 metrics, comparisons |
| Recruitment Analysis | Market values, contract expiry, scouting targets |
| Injury Analysis | Injury risk, workload, minutes tracking |
| FPL Intelligence | Value picks, ownership, predicted points, transfers |
| Predictive Analytics | Match outcomes, performance forecasts |

## Design System

- **Theme**: Dark Mode / Tech-Noir / Glassmorphism
- **Typography**: IBM Plex Mono (KPIs), Cairo (headers/body)
- **Palette**: Arsenal Red `#EF0107`, Neon Cyan `#00F0FF`, Dark Navy `#0A1C3E`

## Models

| Model | Target | Algorithm |
|-------|--------|-----------|
| Match Predictor | H/D/A | XGBoost, RF, Logistic Regression |
| Player Performance | xG, xA, Points | XGBoost, RF |
| Injury Risk | Probability | XGBoost, Gradient Boosting, RF |
| FPL Forecaster | GW Points | XGBoost, Ridge, Linear |

## License

MIT — Built for portfolio and educational purposes.
=======
# arsenal-analytics-platform
>>>>>>> d3c431fdb2bab07979e0cf4395930e136f8ea02a
