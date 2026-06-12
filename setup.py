"""
Database setup — creates the SQLite/PostgreSQL star schema database
with all dimension and fact tables, indexes, and seed data.
"""

from typing import List

import pandas as pd
from sqlalchemy import (
    Column, Date, DateTime, Float, ForeignKey, Integer, String, Boolean,
    create_engine, Table, MetaData, Text, event, text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

from config.config import config
from config.logging_config import get_logger

from database.schema import ALL_TABLES, DIM_DATES


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode and foreign keys for SQLite."""
    import sqlite3
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class StarSchema:
    """Manages the star schema database lifecycle."""

    def __init__(self, db_path: str = ""):
        self.logger = get_logger("database")
        self.db_path = db_path or config.DB_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.metadata = MetaData()
        self._table_objects = {}
        self.logger.info(f"Database: sqlite:///{self.db_path}")

    def create_all_tables(self):
        """Create all tables defined in the schema."""
        for table_def in ALL_TABLES:
            columns = []
            for col_name, col_type, fk_str in zip(
                table_def.columns, table_def.types, 
                table_def.foreign_keys + [""] * (len(table_def.columns) - len(table_def.foreign_keys))
            ):
                is_pk = col_name == table_def.primary_key
                sqlalchemy_type = self._parse_type(col_type)
                col = Column(
                    col_name,
                    sqlalchemy_type,
                    primary_key=is_pk,
                    autoincrement=is_pk and "INTEGER" in col_type.upper(),
                )
                columns.append(col)

            table = Table(table_def.name, self.metadata, *columns)
            self._table_objects[table_def.name] = table

        # Add foreign keys after table creation
        for table_def in ALL_TABLES:
            for fk_stmt in table_def.foreign_keys:
                if fk_stmt:
                    pass

        self.metadata.create_all(self.engine)
        self.logger.info(f"Created {len(ALL_TABLES)} tables")

    def _parse_type(self, type_str: str):
        mapping = {
            "INTEGER": Integer,
            "REAL": Float,
            "TEXT": String,
            "DATE": Date,
            "TIMESTAMP": DateTime,
            "BOOLEAN": Boolean,
        }
        base = type_str.split()[0].upper()
        return mapping.get(base, String)

    def seed_dim_dates(self, start_year: int = 2020, end_year: int = 2030):
        """Populate the date dimension with all dates in range."""
        dates = pd.date_range(f"{start_year}-01-01", f"{end_year}-12-31", freq="D")
        rows = []
        for d in dates:
            rows.append({
                "date_id": d.strftime("%Y%m%d"),
                "full_date": d.date(),
                "day": d.day,
                "month": d.month,
                "year": d.year,
                "day_of_week": d.dayofweek,
                "day_name": d.strftime("%A"),
                "month_name": d.strftime("%B"),
                "quarter": d.quarter,
                "is_weekend": d.dayofweek >= 5,
                "season": self._get_season(d.year, d.month),
            })
        df = pd.DataFrame(rows)
        df.to_sql(DIM_DATES.name, self.engine, if_exists="append", index=False)
        self.logger.info(f"Seeded {len(df)} date rows")

    def _get_season(self, year: int, month: int) -> str:
        if month >= 8:
            return f"{year}-{year + 1}"
        return f"{year - 1}-{year}"

    def seed_premier_league_teams(self):
        """Seed 2025/26 Premier League teams."""
        teams = [
            (1, "Arsenal", "ARS", 3, 9825, "Emirates Stadium", 1886),
            (2, "Aston Villa", "AVL", 7, 10252, "Villa Park", 1874),
            (3, "Bournemouth", "BOU", 91, 10268, "Vitality Stadium", 1890),
            (4, "Brentford", "BRE", 94, 10256, "Gtech Community Stadium", 1889),
            (5, "Brighton", "BRI", 36, 10231, "Amex Stadium", 1901),
            (6, "Chelsea", "CHE", 8, 10261, "Stamford Bridge", 1905),
            (7, "Crystal Palace", "CRY", 31, 10246, "Selhurst Park", 1905),
            (8, "Everton", "EVE", 11, 10262, "Goodison Park", 1878),
            (9, "Fulham", "FUL", 54, 10263, "Craven Cottage", 1879),
            (10, "Ipswich Town", "IPS", 40, 10255, "Portman Road", 1878),
            (11, "Leicester City", "LEI", 26, 10258, "King Power Stadium", 1884),
            (12, "Liverpool", "LIV", 14, 10259, "Anfield", 1892),
            (13, "Manchester City", "MCI", 2, 10260, "Etihad Stadium", 1880),
            (14, "Manchester United", "MUN", 1, 10264, "Old Trafford", 1878),
            (15, "Newcastle United", "NEW", 23, 10253, "St. James' Park", 1892),
            (16, "Nottingham Forest", "NFO", 27, 10254, "City Ground", 1865),
            (17, "Southampton", "SOU", 20, 10266, "St. Mary's Stadium", 1885),
            (18, "Tottenham", "TOT", 6, 10265, "Tottenham Hotspur Stadium", 1882),
            (19, "West Ham", "WHU", 21, 10267, "London Stadium", 1895),
            (20, "Wolves", "WOL", 39, 10257, "Molineux Stadium", 1877),
        ]
        df = pd.DataFrame(teams, columns=[
            "team_id", "team_name", "short_name", "fpl_team_id",
            "fotmob_team_id", "stadium", "founded_year"
        ])
        df.to_sql("dim_teams", self.engine, if_exists="append", index=False)
        self.logger.info(f"Seeded {len(df)} teams")

    def seed_competitions(self):
        """Seed common competitions."""
        comps = [
            (9, "Premier League", "League", "England", False),
            (2, "UEFA Champions League", "Continental Cup", "Europe", True),
            (1, "FA Cup", "Domestic Cup", "England", False),
            (3, "EFL Cup", "Domestic Cup", "England", False),
            (10, "Community Shield", "Super Cup", "England", False),
        ]
        df = pd.DataFrame(comps, columns=[
            "competition_id", "competition_name", "competition_type",
            "country", "is_international"
        ])
        df.to_sql("dim_competitions", self.engine, if_exists="append", index=False)
        self.logger.info(f"Seeded {len(df)} competitions")

    def get_engine(self):
        return self.engine

    def dispose(self):
        self.engine.dispose()


def setup_database():
    """Convenience function: create DB, all tables, seed data."""
    schema = StarSchema()
    schema.create_all_tables()
    schema.seed_dim_dates()
    schema.seed_premier_league_teams()
    schema.seed_competitions()
    return schema


if __name__ == "__main__":
    db = setup_database()
    print(f"Database created at {config.DB_PATH}")
