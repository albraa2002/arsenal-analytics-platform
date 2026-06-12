"""
Understat extractor — scrapes xG, xGA, xPTS, shot maps, and player shooting
data via the Understat API endpoint (JSON embedded in page scripts).
"""

import json
import re
from typing import Any, Dict, List, Optional

import pandas as pd

from config.config import config
from scripts.extraction.base_extractor import BaseExtractor


class UnderstatExtractor(BaseExtractor):
    """Extracts advanced expected-goal data from Understat."""

    def __init__(self):
        super().__init__("understat")

    def extract(self, **kwargs) -> Dict[str, pd.DataFrame]:
        results: Dict[str, pd.DataFrame] = {}

        try:
            results["team_match_data"] = self.extract_team_matches()
        except Exception as exc:
            self.logger.error(f"team_match_data failed: {exc}")

        try:
            results["player_shooting"] = self.extract_player_shooting()
        except Exception as exc:
            self.logger.error(f"player_shooting failed: {exc}")

        try:
            results["league_table"] = self.extract_league_data()
        except Exception as exc:
            self.logger.error(f"league_table failed: {exc}")

        for name, df in results.items():
            if not df.empty:
                self.save_dataframe(df, f"{name}")

        return results

    def _extract_json_from_page(self, url: str, var_name: str) -> Optional[Any]:
        html = self._request(url).text
        pattern = rf"{var_name}\s*=\s*JSON\.parse\('(.+?)'\)"
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            pattern2 = rf"{var_name}\s*=\s*(\[.+?\]);"
            match2 = re.search(pattern2, html, re.DOTALL)
            if match2:
                return json.loads(match2.group(1))
            return None

        raw = match.group(1)
        raw = raw.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
        raw = raw.replace("\\/", "/").replace("\\n", "\n").replace("\\t", "\t")
        raw = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', "", raw)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raw_clean = raw.encode().decode("unicode_escape")
            return json.loads(raw_clean)

    def extract_team_matches(self) -> pd.DataFrame:
        data = self._extract_json_from_page(
            config.UNDERSTAT_TEAM_URL, "teamsData"
        )
        if not data:
            self.logger.warning("No teamsData found on Understat team page")
            return pd.DataFrame()

        rows = []
        ars_data = None
        for team_name, team_info in data.items():
            if "Arsenal" in team_name or "arsenal" in team_name.lower():
                ars_data = team_info
                break
        if not ars_data:
            for team_name, team_info in data.items():
                ars_data = team_info
                break

        if not ars_data:
            return pd.DataFrame()

        history = ars_data.get("history", [])
        for match in history:
            row = {
                "match_id": match.get("id"),
                "opponent": match.get("h_title") if match.get("h_title") != "Arsenal" else match.get("a_title"),
                "is_home": match.get("h_title") == "Arsenal",
                "xG": float(match.get("xG", 0)),
                "xGA": float(match.get("xGA", 0)),
                "scored": int(match.get("goals", 0)),
                "conceded": int(match.get("xGA", 0)),
                "result": match.get("result", ""),
                "date": match.get("date"),
                "season": config.CURRENT_SEASON,
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df

    def extract_player_shooting(self) -> pd.DataFrame:
        data = self._extract_json_from_page(
            config.UNDERSTAT_LEAGUE, "playersData"
        )
        if not data:
            self.logger.warning("No playersData found")
            return pd.DataFrame()

        rows = []
        for player_id, info in data.items():
            if isinstance(info, dict) and info.get("team_title") == "Arsenal":
                rows.append({
                    "player_id": player_id,
                    "player_name": info.get("player_name", ""),
                    "team": info.get("team_title", ""),
                    "games": info.get("games", 0),
                    "time": info.get("time", 0),
                    "goals": info.get("goals", 0),
                    "xG": info.get("xG", 0),
                    "shots": info.get("shots", 0),
                    "key_passes": info.get("key_passes", 0),
                    "xA": info.get("xGAssists", 0),
                    "xG_per_shot": info.get("xGShot", 0),
                    "assists": info.get("assists", 0),
                    "season": config.CURRENT_SEASON,
                })

        return pd.DataFrame(rows)

    def extract_league_data(self) -> pd.DataFrame:
        data = self._extract_json_from_page(
            config.UNDERSTAT_LEAGUE, "teamsData"
        )
        if not data:
            return pd.DataFrame()

        rows = []
        for team_name, team_info in data.items():
            if isinstance(team_info, dict):
                rows.append({
                    "team": team_name,
                    "xG": team_info.get("xG", 0),
                    "xGA": team_info.get("xGA", 0),
                    "xPTS": team_info.get("xpts", 0),
                    "pts": team_info.get("pts", 0),
                    "scored": team_info.get("scored", 0),
                    "missed": team_info.get("missed", 0),
                    "season": config.CURRENT_SEASON,
                })

        return pd.DataFrame(rows)
