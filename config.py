"""
Project configuration module.

Centralizes all paths, API endpoints, DB credentials,
and football-specific constants for the analytics platform.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class Paths:
    root: Path = Path(__file__).resolve().parent.parent

    # Data layers
    raw: Path = field(default_factory=lambda: Paths.root / "data" / "raw")
    processed: Path = field(default_factory=lambda: Paths.root / "data" / "processed")
    features: Path = field(default_factory=lambda: Paths.root / "data" / "features")
    final: Path = field(default_factory=lambda: Paths.root / "data" / "final")

    # Source-specific raw
    fbref: Path = field(default_factory=lambda: Paths.raw / "fbref")
    understat: Path = field(default_factory=lambda: Paths.raw / "understat")
    fpl: Path = field(default_factory=lambda: Paths.raw / "fpl")
    statsbomb: Path = field(default_factory=lambda: Paths.raw / "statsbomb")
    fotmob: Path = field(default_factory=lambda: Paths.raw / "fotmob")
    transfermarkt: Path = field(default_factory=lambda: Paths.raw / "transfermarkt")

    # Outputs
    plots: Path = field(default_factory=lambda: Paths.root / "outputs" / "plots")
    reports: Path = field(default_factory=lambda: Paths.root / "outputs" / "reports")
    models: Path = field(default_factory=lambda: Paths.root / "outputs" / "models")
    dashboards: Path = field(default_factory=lambda: Paths.root / "dashboards")
    database: Path = field(default_factory=lambda: Paths.root / "database")


@dataclass(frozen=True)
class Config:
    paths: Paths = field(default_factory=Paths)

    # Arsenal specific
    ARSENAL_TEAM_ID: int = 42
    FPL_TEAM_ID: int = 3
    FBREF_TEAM_SLUG: str = "Arsenal"
    UNDERSTAT_TEAM: str = "Arsenal"
    STATSBOMB_TEAM: str = "Arsenal Women" if False else "Arsenal"

    # Seasons
    CURRENT_SEASON: str = "2025-2026"
    CURRENT_FPL_SEASON: str = "2025-26"
    STATSBOMB_SEASONS: List[int] = field(default_factory=lambda: [2025])

    # API endpoints
    FPL_BASE_URL: str = "https://fantasy.premierleague.com/api"
    FPL_BOOTSTRAP: str = "https://fantasy.premierleague.com/api/bootstrap-static/"
    FPL_FIXTURES: str = "https://fantasy.premierleague.com/api/fixtures/"
    FPL_EVENT: str = "https://fantasy.premierleague.com/api/event/{gw}/live/"
    FPL_PLAYER_SUMMARY: str = "https://fantasy.premierleague.com/api/element-summary/{player_id}/"

    UNDERSTAT_BASE: str = "https://understat.com"
    UNDERSTAT_LEAGUE: str = "https://understat.com/league/EPL"
    UNDERSTAT_TEAM_URL: str = "https://understat.com/team/Arsenal"
    UNDERSTAT_MATCH_URL: str = "https://understat.com/match/{match_id}"

    FBREF_BASE: str = "https://fbref.com/en/comps/9"
    FBREF_SQUAD_URL: str = "https://fbref.com/en/squads/{team_id}/{season}"

    STATSBOMB_GITHUB: str = "https://raw.githubusercontent.com/statsbomb/open-data/master"
    STATSBOMB_EVENTS: str = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json"
    STATSBOMB_MATCHES: str = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/{competition_id}/{season_id}.json"

    FOTMOB_BASE: str = "https://www.fotmob.com/api"
    FOTMOB_MATCHES: str = "https://www.fotmob.com/api/matches"
    FOTMOB_TEAM: str = "https://www.fotmob.com/api/teams"
    FOTMOB_LEAGUE: str = "https://www.fotmob.com/api/leagues"
    FOTMOB_PLAYER: str = "https://www.fotmob.com/api/playerData"

    TRANSFERMARKT_BASE: str = "https://www.transfermarkt.com"

    # Database
    DB_TYPE: str = "sqlite"
    DB_NAME: str = "arsenal_analytics.db"
    DB_PATH: str = ""

    def __post_init__(self):
        object.__setattr__(self, "DB_PATH", str(self.paths.database / self.DB_NAME))

    # Rate limiting
    REQUEST_DELAY: float = 3.0
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 2.0

    # Football constants
    PITCH_LENGTH: int = 105
    PITCH_WIDTH: int = 68
    GOAL_X: float = 105.0
    GOAL_Y: float = 34.0
    CENTER_CIRCLE_R: float = 9.15

    # Arsenal specific metadata
    ARSENAL_STADIUM: str = "Emirates Stadium"
    ARSENAL_MANAGER: str = "Mikel Arteta"

    # Feature engineering
    PPDA_DENOMINATOR_PASSES: int = 5
    ROLLING_WINDOWS: List[int] = field(default_factory=lambda: [3, 5, 10])

    # FPL
    FPL_POSITION_MAP: Dict[int, str] = field(default_factory=lambda: {
        1: "Goalkeeper",
        2: "Defender",
        3: "Midfielder",
        4: "Forward",
    })

    # Understat shot type mapping
    SHOT_TYPE_MAP: Dict[str, str] = field(default_factory=lambda: {
        "Head": "Header",
        "LeftFoot": "Left Foot",
        "RightFoot": "Right Foot",
        "OtherBodyPart": "Other",
    })


# Singleton
config = Config()
