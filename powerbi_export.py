"""
Power BI preparation — exports final clean datasets to CSV, SQLite,
and generates data documentation.
"""

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import create_engine

from config.config import config
from config.logging_config import get_logger


class PowerBIExporter:
    """Exports datasets for Power BI consumption."""

    def __init__(self, logger_name: str = "powerbi_export"):
        self.logger = get_logger(logger_name)
        self.final_dir = config.paths.final
        self.final_dir.mkdir(parents=True, exist_ok=True)

    def export_to_csv(self, datasets: Dict[str, pd.DataFrame]):
        """Export all datasets to CSV files."""
        for name, df in datasets.items():
            path = self.final_dir / f"{name}.csv"
            df.to_csv(path, index=False)
            self.logger.info(f"CSV export: {path} ({len(df)} rows)")

    def export_to_sqlite(self, datasets: Dict[str, pd.DataFrame], db_name: str = ""):
        """Export all datasets to SQLite database."""
        db_path = config.paths.database / (db_name or "powerbi_arsenal.db")
        engine = create_engine(f"sqlite:///{db_path}")
        for name, df in datasets.items():
            table_name = name.replace("-", "_").replace(" ", "_").lower()
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            self.logger.info(f"SQLite export: {db_path} → {table_name} ({len(df)} rows)")
        engine.dispose()

    def export_star_schema(self, star_data: Dict[str, pd.DataFrame], db_path: str = ""):
        """Export star schema tables to the analytics database."""
        db = db_path or config.DB_PATH
        engine = create_engine(f"sqlite:///{db}")
        for table_name, df in star_data.items():
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            self.logger.info(f"Star schema: {table_name} ({len(df)} rows)")
        engine.dispose()

    def generate_data_dictionary(self, datasets: Dict[str, pd.DataFrame]) -> str:
        """Generate markdown data dictionary for Power BI documentation."""
        lines = [
            "# Arsenal Analytics — Data Dictionary\n",
            f"Generated for Power BI | Season {config.CURRENT_SEASON}\n",
            "---\n",
        ]

        for name, df in datasets.items():
            lines.append(f"## {name}\n")
            lines.append(f"- **Rows**: {len(df)}")
            lines.append(f"- **Columns**: {len(df.columns)}\n")
            lines.append("| Column | Dtype | Non-Null | Description |")
            lines.append("|--------|-------|----------|-------------|")
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null = df[col].notna().sum()
                desc = self._describe_column(col)
                lines.append(f"| {col} | {dtype} | {non_null} | {desc} |")
            lines.append("")

        return "\n".join(lines)

    def generate_relationship_doc(self) -> str:
        """Generate star-schema relationship documentation."""
        return """# Star Schema Relationships

## Dimension Tables (lookup tables)

| Table | Key | Description |
|-------|-----|-------------|
| dim_players | player_id | Unique player identifier across all sources |
| dim_teams | team_id | Premier League teams |
| dim_matches | match_id | Match-level dimension |
| dim_competitions | competition_id | Competition/league metadata |
| dim_dates | date_id | Calendar dimension (YYYYMMDD) |

## Fact Tables (measure tables)

| Table | Key | Foreign Keys | Description |
|-------|-----|--------------|-------------|
| fact_matches | fact_match_id | match_id, date_id, competition_id, home_team_id, away_team_id | Match-level stats & xG |
| fact_player_match_stats | fact_player_match_id | player_id, match_id, date_id, team_id | Per-player per-match stats |
| fact_shots | shot_id | match_id, player_id, team_id | Every shot with xG & coordinates |
| fact_passes | pass_id | match_id, player_id, team_id | Every pass with location |
| fact_fpl_gameweeks | fact_fpl_id | player_id, date_id | FPL gameweek-level data |

## Relationships (Star Schema)

- dim_matches.match_id → fact_matches.match_id (1:1)
- dim_dates.date_id → fact_matches.date_id (1:many)
- dim_competitions.competition_id → fact_matches.competition_id (1:many)
- dim_teams.team_id → fact_matches.home_team_id (1:many)
- dim_teams.team_id → fact_matches.away_team_id (1:many)
- dim_players.player_id → fact_player_match_stats.player_id (1:many)
- dim_matches.match_id → fact_player_match_stats.match_id (1:many)
- dim_dates.date_id → fact_player_match_stats.date_id (1:many)
- dim_teams.team_id → fact_player_match_stats.team_id (1:many)
- dim_matches.match_id → fact_shots.match_id (1:many)
- dim_players.player_id → fact_shots.player_id (1:many)
- dim_matches.match_id → fact_passes.match_id (1:many)
- dim_players.player_id → fact_passes.player_id (1:many)
- dim_players.player_id → fact_fpl_gameweeks.player_id (1:many)
- dim_dates.date_id → fact_fpl_gameweeks.date_id (1:many)
"""

    def _describe_column(self, col: str) -> str:
        descriptions = {
            "player_name": "Player display name",
            "resolved_name": "Canonical player name after entity resolution",
            "position": "Playing position (GK, DEF, MID, FWD)",
            "minutes": "Total minutes played",
            "goals": "Total goals scored",
            "assists": "Total assists",
            "xG": "Expected goals",
            "xA": "Expected assists",
            "npxG": "Non-penalty expected goals",
            "progressive_passes": "Passes that move the ball towards goal",
            "progressive_carries": "Carries that move the ball towards goal",
            "touches": "Total touches",
            "passes": "Total passes attempted",
            "passes_accurate": "Accurate passes",
            "key_passes": "Passes leading directly to a shot",
            "tackles": "Total tackles",
            "interceptions": "Passes intercepted",
            "blocks": "Shots/passes blocked",
            "clearances": "Defensive clearances",
            "dribbles_completed": "Successful dribbles",
            "fouls": "Fouls committed",
            "fouls_drawn": "Fouls suffered",
            "yellow_cards": "Yellow cards received",
            "red_cards": "Red cards received",
            "saves": "Goalkeeper saves",
            "goals_conceded": "Goals conceded",
            "clean_sheet": "Whether player kept a clean sheet",
            "fpl_points": "Fantasy Premier League points",
            "now_cost": "Current FPL price in £m",
            "selected_by_percent": "FPL ownership percentage",
            "ict_index": "FPL ICT (Influence, Creativity, Threat) index",
            "expected_goals": "FPL expected goals",
            "expected_assists": "FPL expected assists",
            "match_id": "Unique match identifier",
            "date_id": "Date key (YYYYMMDD) for date dimension join",
            "team_name": "Team name",
            "shot_type": "Type of shot (Open Play, Set Piece, etc.)",
            "body_part": "Body part used (Right Foot, Left Foot, Head)",
            "shot_outcome": "Result of shot (Goal, Saved, Blocked, etc.)",
            "statsbomb_xg": "StatsBomb expected goal value",
            "location_x": "X coordinate on pitch (0-120)",
            "location_y": "Y coordinate on pitch (0-80)",
        }
        return descriptions.get(col, f"Raw column: {col}")

    def export_all(
        self,
        csv_datasets: Dict[str, pd.DataFrame],
        sqlite_datasets: Dict[str, pd.DataFrame],
        star_data: Dict[str, pd.DataFrame],
    ):
        """Complete export: CSV + SQLite + documentation."""
        self.export_to_csv(csv_datasets)
        self.export_to_sqlite(sqlite_datasets)
        self.export_star_schema(star_data)

        doc = self.generate_data_dictionary(csv_datasets)
        doc_path = config.paths.docs / "data_dictionary.md"
        doc_path.write_text(doc, encoding="utf-8")

        rel_doc = self.generate_relationship_doc()
        rel_path = config.paths.docs / "relationships.md"
        rel_path.write_text(rel_doc, encoding="utf-8")

        self.logger.info(f"Documentation written to {config.paths.docs}")
        self.logger.info("Power BI export complete")
