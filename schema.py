"""
Star Schema definitions for the Arsenal Football Data Warehouse.

Fact tables:
    fact_matches
    fact_player_match_stats
    fact_shots
    fact_passes
    fact_fpl_gameweeks

Dimension tables:
    dim_players
    dim_teams
    dim_matches
    dim_competitions
    dim_dates
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TableDef:
    name: str
    columns: List[str]
    types: List[str]
    primary_key: str
    foreign_keys: List[str] = field(default_factory=list)


# ── Dimension Tables ──────────────────────────────────────────────

DIM_PLAYERS = TableDef(
    name="dim_players",
    columns=[
        "player_id", "canonical_name", "source_name", "position",
        "age", "nationality", "height", "foot", "market_value_euro",
        "contract_until", "jersey_number", "is_arsenal_player",
        "primary_source", "created_at", "updated_at",
    ],
    types=[
        "INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "TEXT",
        "INTEGER", "TEXT", "REAL", "TEXT", "REAL",
        "TEXT", "INTEGER", "BOOLEAN",
        "TEXT", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="player_id",
)

DIM_TEAMS = TableDef(
    name="dim_teams",
    columns=[
        "team_id", "team_name", "short_name", "fpl_team_id",
        "fotmob_team_id", "stadium", "founded_year",
        "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT", "TEXT", "INTEGER",
        "INTEGER", "TEXT", "INTEGER",
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="team_id",
)

DIM_MATCHES = TableDef(
    name="dim_matches",
    columns=[
        "match_id", "match_date", "kick_off", "competition_id",
        "home_team_id", "away_team_id", "home_score", "away_score",
        "match_week", "stadium", "match_status", "season",
        "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY", "DATE", "TEXT", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "TEXT", "TEXT", "TEXT",
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="match_id",
)

DIM_COMPETITIONS = TableDef(
    name="dim_competitions",
    columns=[
        "competition_id", "competition_name", "competition_type",
        "country", "is_international", "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY", "TEXT", "TEXT",
        "TEXT", "BOOLEAN", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="competition_id",
)

DIM_DATES = TableDef(
    name="dim_dates",
    columns=[
        "date_id", "full_date", "day", "month", "year",
        "day_of_week", "day_name", "month_name", "quarter",
        "is_weekend", "season",
    ],
    types=[
        "TEXT PRIMARY KEY", "DATE", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "TEXT", "TEXT", "INTEGER",
        "BOOLEAN", "TEXT",
    ],
    primary_key="date_id",
)


# ── Fact Tables ───────────────────────────────────────────────────

FACT_MATCHES = TableDef(
    name="fact_matches",
    columns=[
        "fact_match_id", "match_id", "date_id", "competition_id",
        "home_team_id", "away_team_id",
        "home_xG", "away_xG", "home_xGA", "away_xGA",
        "home_possession_pct", "away_possession_pct",
        "home_shots", "away_shots",
        "home_shots_on_target", "away_shots_on_target",
        "home_corners", "away_corners",
        "home_fouls", "away_fouls",
        "home_yellow_cards", "away_yellow_cards",
        "home_red_cards", "away_red_cards",
        "home_ppda", "away_ppda",
        "home_deep_completions", "away_deep_completions",
        "attendance", "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "TEXT", "INTEGER",
        "INTEGER", "INTEGER",
        "REAL", "REAL", "REAL", "REAL",
        "REAL", "REAL",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "REAL", "REAL",
        "INTEGER", "INTEGER",
        "INTEGER", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="fact_match_id",
    foreign_keys=[
        "FOREIGN KEY (match_id) REFERENCES dim_matches(match_id)",
        "FOREIGN KEY (date_id) REFERENCES dim_dates(date_id)",
        "FOREIGN KEY (competition_id) REFERENCES dim_competitions(competition_id)",
        "FOREIGN KEY (home_team_id) REFERENCES dim_teams(team_id)",
        "FOREIGN KEY (away_team_id) REFERENCES dim_teams(team_id)",
    ],
)

FACT_PLAYER_MATCH_STATS = TableDef(
    name="fact_player_match_stats",
    columns=[
        "fact_player_match_id", "player_id", "match_id", "date_id",
        "team_id", "minutes_played", "goals", "assists", "shots",
        "shots_on_target", "passes", "passes_accurate", "key_passes",
        "xG", "xA", "npxG",
        "progressive_passes", "progressive_carries",
        "touches", "touches_defensive_third", "touches_mid_third",
        "touches_attacking_third", "touches_attacking_penalty_area",
        "tackles", "interceptions", "blocks", "clearances",
        "dribbles_attempted", "dribbles_completed",
        "aerial_duels_won", "aerial_duels_lost",
        "fouls", "fouls_drawn", "offsides",
        "yellow_card", "red_card",
        "saves", "goals_conceded", "clean_sheet",
        "fpl_points", "fpl_value", "fpl_selected_pct",
        "rating", "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "INTEGER", "TEXT",
        "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER", "INTEGER",
        "REAL", "REAL", "REAL",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "BOOLEAN",
        "INTEGER", "REAL", "REAL",
        "REAL", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="fact_player_match_id",
    foreign_keys=[
        "FOREIGN KEY (player_id) REFERENCES dim_players(player_id)",
        "FOREIGN KEY (match_id) REFERENCES dim_matches(match_id)",
        "FOREIGN KEY (date_id) REFERENCES dim_dates(date_id)",
        "FOREIGN KEY (team_id) REFERENCES dim_teams(team_id)",
    ],
)

FACT_SHOTS = TableDef(
    name="fact_shots",
    columns=[
        "shot_id", "match_id", "player_id", "team_id",
        "minute", "second", "period",
        "location_x", "location_y",
        "end_location_x", "end_location_y",
        "shot_type", "body_part", "shot_outcome",
        "statsbomb_xg", "goal", "one_on_one",
        "deflected", "first_time", "open_goal",
        "technique", "under_pressure",
        "freeze_frame_available", "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER",
        "REAL", "REAL",
        "REAL", "REAL",
        "TEXT", "TEXT", "TEXT",
        "REAL", "BOOLEAN", "BOOLEAN",
        "BOOLEAN", "BOOLEAN", "BOOLEAN",
        "TEXT", "BOOLEAN",
        "BOOLEAN", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="shot_id",
    foreign_keys=[
        "FOREIGN KEY (match_id) REFERENCES dim_matches(match_id)",
        "FOREIGN KEY (player_id) REFERENCES dim_players(player_id)",
        "FOREIGN KEY (team_id) REFERENCES dim_teams(team_id)",
    ],
)

FACT_PASSES = TableDef(
    name="fact_passes",
    columns=[
        "pass_id", "match_id", "player_id", "team_id",
        "minute", "second", "period",
        "location_x", "location_y",
        "end_location_x", "end_location_y",
        "pass_length", "pass_angle", "pass_type",
        "body_part", "pass_outcome",
        "shot_assist", "goal_assist",
        "cross", "through_ball", "switch",
        "under_pressure", "recipient_player_id",
        "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER",
        "REAL", "REAL",
        "REAL", "REAL",
        "REAL", "REAL", "TEXT",
        "TEXT", "TEXT",
        "BOOLEAN", "BOOLEAN",
        "BOOLEAN", "BOOLEAN", "BOOLEAN",
        "BOOLEAN", "INTEGER",
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="pass_id",
    foreign_keys=[
        "FOREIGN KEY (match_id) REFERENCES dim_matches(match_id)",
        "FOREIGN KEY (player_id) REFERENCES dim_players(player_id)",
        "FOREIGN KEY (team_id) REFERENCES dim_teams(team_id)",
    ],
)

FACT_FPL_GAMEWEEKS = TableDef(
    name="fact_fpl_gameweeks",
    columns=[
        "fact_fpl_id", "fpl_player_id", "player_id", "gameweek",
        "date_id", "minutes", "goals_scored", "assists",
        "clean_sheets", "goals_conceded", "bonus", "bps",
        "total_points", "influence", "creativity", "threat",
        "ict_index", "expected_goals", "expected_assists",
        "expected_goal_involvements", "expected_goals_conceded",
        "value", "transfers_balance", "selected",
        "transfers_in", "transfers_out",
        "season", "created_at",
    ],
    types=[
        "INTEGER PRIMARY KEY AUTOINCREMENT", "INTEGER", "INTEGER", "INTEGER",
        "TEXT", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER", "INTEGER", "INTEGER",
        "INTEGER", "REAL", "REAL", "REAL",
        "REAL", "REAL", "REAL",
        "REAL", "REAL",
        "REAL", "INTEGER", "INTEGER",
        "INTEGER", "INTEGER",
        "TEXT", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ],
    primary_key="fact_fpl_id",
    foreign_keys=[
        "FOREIGN KEY (player_id) REFERENCES dim_players(player_id)",
        "FOREIGN KEY (date_id) REFERENCES dim_dates(date_id)",
    ],
)


# Registry of all tables for automatic creation
ALL_TABLES: List[TableDef] = [
    DIM_PLAYERS,
    DIM_TEAMS,
    DIM_MATCHES,
    DIM_COMPETITIONS,
    DIM_DATES,
    FACT_MATCHES,
    FACT_PLAYER_MATCH_STATS,
    FACT_SHOTS,
    FACT_PASSES,
    FACT_FPL_GAMEWEEKS,
]
