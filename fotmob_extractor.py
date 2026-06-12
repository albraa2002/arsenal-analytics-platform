"""
Fotmob extractor — pulls match details, team data, league tables, and
player stats via the unofficial Fotmob API.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from config.config import config
from scripts.extraction.base_extractor import BaseExtractor


class FotmobExtractor(BaseExtractor):
    """Extracts data from Fotmob's internal API."""

    PREMIER_LEAGUE_ID: int = 47
    ARSENAL_FOTMOB_ID: int = 9825
    SEASON_ID: str = "2025/2026"

    def __init__(self):
        super().__init__("fotmob")

    def extract(self, **kwargs) -> Dict[str, pd.DataFrame]:
        results: Dict[str, pd.DataFrame] = {}

        try:
            results["league_table"] = self._get_league_table()
            if not results["league_table"].empty:
                self.save_dataframe(results["league_table"], "fotmob_league_table")
        except Exception as exc:
            self.logger.error(f"League table failed: {exc}")

        try:
            results["team_matches"] = self._get_team_matches()
            if not results["team_matches"].empty:
                self.save_dataframe(results["team_matches"], "fotmob_team_matches")
        except Exception as exc:
            self.logger.error(f"Team matches failed: {exc}")

        try:
            results["team_players"] = self._get_team_players()
            if not results["team_players"].empty:
                self.save_dataframe(results["team_players"], "fotmob_team_players")
        except Exception as exc:
            self.logger.error(f"Team players failed: {exc}")

        return results

    def _get_league_table(self) -> pd.DataFrame:
        params = {"id": self.PREMIER_LEAGUE_ID, "season": self.SEASON_ID}
        data = self._request_json(config.FOTMOB_LEAGUE, params)
        rows = []

        for table_data in data.get("table", []):
            for entry in table_data.get("data", {}).get("table", []):
                rows.append({
                    "position": entry.get("idx"),
                    "team_id": entry.get("id"),
                    "team_name": entry.get("name", ""),
                    "matches": entry.get("matches", 0),
                    "wins": entry.get("wins", 0),
                    "draws": entry.get("draws", 0),
                    "losses": entry.get("losses", 0),
                    "goals_scored": entry.get("scoresStr", "").split("-")[0].strip() if entry.get("scoresStr") else 0,
                    "goals_conceded": entry.get("scoresStr", "").split("-")[1].strip() if entry.get("scoresStr") else 0,
                    "goal_diff": entry.get("goalConDiff", 0),
                    "points": entry.get("pts", 0),
                    "form": entry.get("form", ""),
                    "season": self.SEASON_ID,
                })
        return pd.DataFrame(rows)

    def _get_team_matches(self) -> pd.DataFrame:
        params = {"id": self.ARSENAL_FOTMOB_ID}
        data = self._request_json(config.FOTMOB_TEAM, params)
        rows = []

        for match in data.get("matches", {}).get("allMatches", []):
            rows.append({
                "match_id": match.get("id"),
                "league_id": match.get("leagueId"),
                "season": match.get("season", self.SEASON_ID),
                "round": match.get("round"),
                "round_name": match.get("roundName", ""),
                "home_team_id": match.get("home", {}).get("id") if match.get("home") else None,
                "home_team_name": match.get("home", {}).get("name", "") if match.get("home") else "",
                "away_team_id": match.get("away", {}).get("id") if match.get("away") else None,
                "away_team_name": match.get("away", {}).get("name", "") if match.get("away") else "",
                "home_score": match.get("home", {}).get("score", 0) if match.get("home") else 0,
                "away_score": match.get("away", {}).get("score", 0) if match.get("away") else 0,
                "status": match.get("status", {}).get("reason") if match.get("status") else "",
                "date": match.get("status", {}).get("utcTime") if match.get("status") else "",
            })

        return pd.DataFrame(rows)

    def _get_team_players(self) -> pd.DataFrame:
        params = {"id": self.ARSENAL_FOTMOB_ID}
        data = self._request_json(config.FOTMOB_TEAM, params)
        rows = []

        for squad_entry in data.get("squad", []):
            for player in squad_entry.get("players", []):
                rows.append({
                    "player_id": player.get("id"),
                    "player_name": player.get("name", ""),
                    "position": squad_entry.get("strRole", ""),
                    "jersey_number": player.get("jerseyNumber"),
                    "age": player.get("age"),
                    "height": player.get("height"),
                    "foot": player.get("foot", ""),
                    "nationality": player.get("nationality", ""),
                    "contract_until": player.get("contractUntil", ""),
                    "market_value": player.get("marketValue", ""),
                    "team_id": self.ARSENAL_FOTMOB_ID,
                    "season": self.SEASON_ID,
                })

        return pd.DataFrame(rows)
