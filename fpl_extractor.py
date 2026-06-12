"""
FPL API extractor — pulls bootstrap static data, live gameweek data,
fixtures, and player-specific summaries from the official FPL API.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from config.config import config
from scripts.extraction.base_extractor import BaseExtractor


class FPLExtractor(BaseExtractor):
    """Extracts Fantasy Premier League data via the public API."""

    def __init__(self):
        super().__init__("fpl", cache_ttl=300)

    def extract(self, **kwargs) -> Dict[str, pd.DataFrame]:
        results: Dict[str, pd.DataFrame] = {}

        try:
            bootstrap = self._request_json(config.FPL_BOOTSTRAP)
        except Exception as exc:
            self.logger.error(f"Bootstrap data failed: {exc}")
            return results

        if "elements" in bootstrap:
            results["players"] = self._parse_players(bootstrap["elements"])
            self.save_dataframe(results["players"], "fpl_players")

        if "teams" in bootstrap:
            results["teams"] = pd.DataFrame(bootstrap["teams"])
            self.save_dataframe(results["teams"], "fpl_teams")

        if "events" in bootstrap:
            results["events"] = pd.DataFrame(bootstrap["events"])
            self.save_dataframe(results["events"], "fpl_events")

        try:
            fixtures = self._request_json(config.FPL_FIXTURES)
            results["fixtures"] = pd.DataFrame(fixtures)
            self.save_dataframe(results["fixtures"], "fpl_fixtures")
        except Exception as exc:
            self.logger.error(f"Fixtures failed: {exc}")

        try:
            gws = self._extract_all_gameweeks()
            if not gws.empty:
                results["gameweek_history"] = gws
                self.save_dataframe(gws, "fpl_gameweek_history")
        except Exception as exc:
            self.logger.error(f"Gameweek history failed: {exc}")

        try:
            player_details = self._extract_player_details()
            if not player_details.empty:
                results["player_details"] = player_details
                self.save_dataframe(player_details, "fpl_player_details")
        except Exception as exc:
            self.logger.error(f"Player details failed: {exc}")

        try:
            results["arsenal_players"] = self._filter_arsenal(results)
            if not results["arsenal_players"].empty:
                self.save_dataframe(results["arsenal_players"], "fpl_arsenal_players")
        except Exception as exc:
            self.logger.error(f"Arsenal filter failed: {exc}")

        return results

    def _parse_players(self, elements: List[Dict]) -> pd.DataFrame:
        rows = []
        for e in elements:
            rows.append({
                "fpl_id": e.get("id"),
                "first_name": e.get("first_name", ""),
                "second_name": e.get("second_name", ""),
                "web_name": e.get("web_name", ""),
                "team_fpl_id": e.get("team"),
                "element_type": e.get("element_type"),
                "position": config.FPL_POSITION_MAP.get(e.get("element_type", 0), "Unknown"),
                "now_cost": e.get("now_cost", 0) / 10.0,
                "selected_by_percent": float(e.get("selected_by_percent", 0)),
                "form": float(e.get("form", 0)),
                "points_per_game": float(e.get("points_per_game", 0)),
                "total_points": e.get("total_points", 0),
                "minutes": e.get("minutes", 0),
                "goals_scored": e.get("goals_scored", 0),
                "assists": e.get("assists", 0),
                "clean_sheets": e.get("clean_sheets", 0),
                "goals_conceded": e.get("goals_conceded", 0),
                "own_goals": e.get("own_goals", 0),
                "penalties_saved": e.get("penalties_saved", 0),
                "penalties_missed": e.get("penalties_missed", 0),
                "yellow_cards": e.get("yellow_cards", 0),
                "red_cards": e.get("red_cards", 0),
                "saves": e.get("saves", 0),
                "bonus": e.get("bonus", 0),
                "bps": e.get("bps", 0),
                "influence": float(e.get("influence", 0)),
                "creativity": float(e.get("creativity", 0)),
                "threat": float(e.get("threat", 0)),
                "ict_index": float(e.get("ict_index", 0)),
                "expected_goals": float(e.get("expected_goals", 0)),
                "expected_assists": float(e.get("expected_assists", 0)),
                "expected_goal_involvements": float(e.get("expected_goal_involvements", 0)),
                "expected_goals_conceded": float(e.get("expected_goals_conceded", 0)),
                "starts": e.get("starts", 0),
                "code": e.get("code"),
                "season": config.CURRENT_FPL_SEASON,
            })
        return pd.DataFrame(rows)

    def _extract_all_gameweeks(self) -> pd.DataFrame:
        bootstrap = self._request_json(config.FPL_BOOTSTRAP)
        num_gws = len(bootstrap.get("events", []))
        all_rows = []

        for gw in range(1, num_gws + 1):
            try:
                url = config.FPL_EVENT.format(gw=gw)
                gw_data = self._request_json(url)
                for element in gw_data.get("elements", []):
                    all_rows.append({
                        "fpl_id": element.get("id"),
                        "gameweek": gw,
                        "minutes": element.get("stats", {}).get("minutes", 0),
                        "goals_scored": element.get("stats", {}).get("goals_scored", 0),
                        "assists": element.get("stats", {}).get("assists", 0),
                        "clean_sheets": element.get("stats", {}).get("clean_sheets", 0),
                        "goals_conceded": element.get("stats", {}).get("goals_conceded", 0),
                        "bonus": element.get("stats", {}).get("bonus", 0),
                        "total_points": element.get("stats", {}).get("total_points", 0),
                        "expected_goals": float(element.get("explain", [{}])[0].get("stats", [{}])[0].get("value", 0)) if element.get("explain") else 0,
                        "expected_assists": float(element.get("explain", [{}])[0].get("stats", [{}])[1].get("value", 0)) if element.get("explain") and len(element["explain"][0].get("stats", [])) > 1 else 0,
                        "season": config.CURRENT_FPL_SEASON,
                    })
            except Exception as exc:
                self.logger.warning(f"GW {gw} live data failed: {exc}")

        return pd.DataFrame(all_rows)

    def _extract_player_details(self) -> pd.DataFrame:
        bootstrap = self._request_json(config.FPL_BOOTSTRAP)
        player_ids = [e["id"] for e in bootstrap.get("elements", []) if e.get("team") == config.FPL_TEAM_ID]
        all_rows = []

        for pid in player_ids:
            try:
                data = self._request_json(config.FPL_PLAYER_SUMMARY.format(player_id=pid))
                for fixture in data.get("history", []):
                    all_rows.append({
                        "fpl_id": pid,
                        "gameweek": fixture.get("round"),
                        "opponent_team": fixture.get("opponent_team"),
                        "total_points": fixture.get("total_points", 0),
                        "minutes": fixture.get("minutes", 0),
                        "goals_scored": fixture.get("goals_scored", 0),
                        "assists": fixture.get("assists", 0),
                        "clean_sheets": fixture.get("clean_sheets", 0),
                        "goals_conceded": fixture.get("goals_conceded", 0),
                        "bonus": fixture.get("bonus", 0),
                        "bps": fixture.get("bps", 0),
                        "influence": float(fixture.get("influence", 0)),
                        "creativity": float(fixture.get("creativity", 0)),
                        "threat": float(fixture.get("threat", 0)),
                        "ict_index": float(fixture.get("ict_index", 0)),
                        "expected_goals": float(fixture.get("expected_goals", 0)),
                        "expected_assists": float(fixture.get("expected_assists", 0)),
                        "expected_goal_involvements": float(fixture.get("expected_goal_involvements", 0)),
                        "expected_goals_conceded": float(fixture.get("expected_goals_conceded", 0)),
                        "value": fixture.get("value", 0) / 10.0,
                        "transfers_balance": fixture.get("transfers_balance", 0),
                        "selected": fixture.get("selected", 0),
                        "transfers_in": fixture.get("transfers_in", 0),
                        "transfers_out": fixture.get("transfers_out", 0),
                        "season": config.CURRENT_FPL_SEASON,
                    })
            except Exception as exc:
                self.logger.warning(f"Player {pid} summary failed: {exc}")

        return pd.DataFrame(all_rows)

    def _filter_arsenal(self, results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        if "players" not in results:
            return pd.DataFrame()
        players = results["players"]
        return players[players["team_fpl_id"] == config.FPL_TEAM_ID].copy()
