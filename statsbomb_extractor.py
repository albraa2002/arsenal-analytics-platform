"""
StatsBomb Open Data extractor — downloads event, match, and lineup data
from the official StatsBomb GitHub repository.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from config.config import config
from scripts.extraction.base_extractor import BaseExtractor


class StatsBombExtractor(BaseExtractor):
    """Downloads and parses StatsBomb open-data events."""

    COMPETITIONS_URL: str = (
        "https://raw.githubusercontent.com/statsbomb/open-data/master/data/"
        "competitions.json"
    )

    def __init__(self):
        super().__init__("statsbomb")

    def extract(self, **kwargs) -> Dict[str, pd.DataFrame]:
        results: Dict[str, pd.DataFrame] = {}

        try:
            matches = self._load_all_matches()
            if not matches.empty:
                results["matches"] = matches
                self.save_dataframe(matches, "statsbomb_matches")
                self.logger.info(f"Extracted {len(matches)} StatsBomb matches")
        except Exception as exc:
            self.logger.error(f"Match extraction failed: {exc}")

        try:
            events = self._load_all_events(matches if not matches.empty else None)
            if not events.empty:
                results["events"] = events
                self.save_dataframe(events, "statsbomb_events")
                self.logger.info(f"Extracted {len(events)} StatsBomb events")
        except Exception as exc:
            self.logger.error(f"Event extraction failed: {exc}")

        try:
            lineups = self._load_all_lineups(matches if not matches.empty else None)
            if not lineups.empty:
                results["lineups"] = lineups
                self.save_dataframe(lineups, "statsbomb_lineups")
                self.logger.info(f"Extracted {len(lineups)} StatsBomb lineups")
        except Exception as exc:
            self.logger.error(f"Lineup extraction failed: {exc}")

        return results

    def _load_competitions(self) -> List[Dict]:
        resp = requests.get(self.COMPETITIONS_URL, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _load_all_matches(self) -> pd.DataFrame:
        competitions = self._load_competitions()
        all_rows = []

        for comp in competitions:
            comp_id = comp["competition_id"]
            season_id = comp["season_id"]
            url = f"{config.STATSBOMB_MATCHES.format(competition_id=comp_id, season_id=season_id)}"
            try:
                matches_data = requests.get(url, timeout=30).json()
                for match in matches_data:
                    home = match.get("home_team", {})
                    away = match.get("away_team", {})
                    competition = match.get("competition", {})
                    season = match.get("season", {})

                    all_rows.append({
                        "match_id": match.get("match_id"),
                        "match_date": match.get("match_date"),
                        "kick_off": match.get("kick_off"),
                        "competition_id": comp_id,
                        "competition_name": competition.get("competition_name", ""),
                        "season_id": season_id,
                        "season_name": season.get("season_name", ""),
                        "home_team_id": home.get("home_team_id"),
                        "home_team_name": home.get("home_team_name", ""),
                        "away_team_id": away.get("away_team_id"),
                        "away_team_name": away.get("away_team_name", ""),
                        "home_score": match.get("home_score", 0),
                        "away_score": match.get("away_score", 0),
                        "match_status": match.get("match_status", ""),
                        "match_week": match.get("match_week"),
                        "stadium": match.get("stadium", {}).get("name", "") if match.get("stadium") else "",
                    })
            except Exception as exc:
                self.logger.warning(f"Failed matches for comp {comp_id} season {season_id}: {exc}")

        return pd.DataFrame(all_rows)

    def _load_all_events(self, matches: Optional[pd.DataFrame]) -> pd.DataFrame:
        if matches is None or matches.empty:
            return pd.DataFrame()

        match_ids = matches["match_id"].dropna().unique().tolist()
        all_events = []

        for mid in match_ids[:50]:
            url = config.STATSBOMB_EVENTS.format(match_id=mid)
            try:
                events_data = requests.get(url, timeout=30).json()
                for event in events_data:
                    flat = self._flatten_event(event)
                    flat["match_id"] = mid
                    all_events.append(flat)
            except Exception as exc:
                self.logger.warning(f"Events for match {mid} failed: {exc}")

        if not all_events:
            return pd.DataFrame()
        return pd.DataFrame(all_events)

    def _flatten_event(self, event: Dict) -> Dict[str, Any]:
        location = event.get("location", [None, None])
        end_location = event.get("pass", {}).get("end_location", [None, None])
        freeze_frame = event.get("shot", {}).get("freeze_frame", [])

        return {
            "event_id": event.get("id"),
            "event_type": event.get("type", {}).get("name", ""),
            "minute": event.get("minute"),
            "second": event.get("second"),
            "period": event.get("period"),
            "possession": event.get("possession"),
            "possession_team_id": event.get("possession_team", {}).get("id") if event.get("possession_team") else None,
            "possession_team_name": event.get("possession_team", {}).get("name") if event.get("possession_team") else "",
            "team_id": event.get("team", {}).get("id") if event.get("team") else None,
            "team_name": event.get("team", {}).get("name") if event.get("team") else "",
            "player_id": event.get("player", {}).get("id") if event.get("player") else None,
            "player_name": event.get("player", {}).get("name") if event.get("player") else "",
            "location_x": location[0] if location else None,
            "location_y": location[1] if location else None,
            "end_location_x": end_location[0] if end_location else None,
            "end_location_y": end_location[1] if end_location else None,
            "pass_length": event.get("pass", {}).get("length"),
            "pass_angle": event.get("pass", {}).get("angle"),
            "pass_type": event.get("pass", {}).get("type", {}).get("name") if event.get("pass") else None,
            "pass_body_part": event.get("pass", {}).get("body_part", {}).get("name") if event.get("pass") else None,
            "pass_outcome": event.get("pass", {}).get("outcome", {}).get("name") if event.get("pass") else None,
            "pass_recipient": event.get("pass", {}).get("recipient", {}).get("name") if event.get("pass") else "",
            "pass_shot_assist": event.get("pass", {}).get("shot_assist", False),
            "pass_goal_assist": event.get("pass", {}).get("goal_assist", False),
            "pass_cross": event.get("pass", {}).get("cross", False),
            "pass_through_ball": event.get("pass", {}).get("through_ball", False),
            "pass_switch": event.get("pass", {}).get("switch", False),
            "carry_end_location_x": event.get("carry", {}).get("end_location", [None, None])[0] if event.get("carry") else None,
            "carry_end_location_y": event.get("carry", {}).get("end_location", [None, None])[1] if event.get("carry") else None,
            "shot_type": event.get("shot", {}).get("type", {}).get("name") if event.get("shot") else None,
            "shot_body_part": event.get("shot", {}).get("body_part", {}).get("name") if event.get("shot") else None,
            "shot_outcome": event.get("shot", {}).get("outcome", {}).get("name") if event.get("shot") else None,
            "shot_statsbomb_xg": event.get("shot", {}).get("statsbomb_xg"),
            "shot_one_on_one": event.get("shot", {}).get("one_on_one", False),
            "shot_deflected": event.get("shot", {}).get("deflected", False),
            "shot_technique": event.get("shot", {}).get("technique", {}).get("name") if event.get("shot") else None,
            "shot_first_time": event.get("shot", {}).get("first_time", False),
            "shot_open_goal": event.get("shot", {}).get("open_goal", False),
            "dribble_outcome": event.get("dribble", {}).get("outcome", {}).get("name") if event.get("dribble") else None,
            "dribble_overrun": event.get("dribble", {}).get("overrun", False) if event.get("dribble") else None,
            "dribble_nutmeg": event.get("dribble", {}).get("nutmeg", False) if event.get("dribble") else None,
            "duel_type": event.get("duel", {}).get("type", {}).get("name") if event.get("duel") else None,
            "duel_outcome": event.get("duel", {}).get("outcome", {}).get("name") if event.get("duel") else None,
            "clearance_aerial_won": event.get("clearance", {}).get("aerial_won", False) if event.get("clearance") else None,
            "ball_recovery_recovery": event.get("ball_recovery", {}).get("recovery", False) if event.get("ball_recovery") else None,
            "ball_recovery_offensive": event.get("ball_recovery", {}).get("offensive", False) if event.get("ball_recovery") else None,
            "counterpress": event.get("counterpress", False),
            "under_pressure": event.get("under_pressure", False),
            "foul_won_defensive": event.get("foul_won", {}).get("defensive", False) if event.get("foul_won") else None,
            "foul_won_offensive": event.get("foul_won", {}).get("offensive", False) if event.get("foul_won") else None,
            "bad_behaviour_card": event.get("bad_behaviour", {}).get("card", {}).get("name") if event.get("bad_behaviour") else None,
            "substitution_replacement": event.get("substitution", {}).get("replacement", {}).get("name") if event.get("substitution") else "",
            "substitution_outcome": event.get("substitution", {}).get("outcome", {}).get("name") if event.get("substitution") else None,
            "goalkeeper_type": event.get("goalkeeper", {}).get("type", {}).get("name") if event.get("goalkeeper") else None,
            "goalkeeper_outcome": event.get("goalkeeper", {}).get("outcome", {}).get("name") if event.get("goalkeeper") else None,
            "goalkeeper_shot_saved_off_target": event.get("goalkeeper", {}).get("shot_saved_off_target", False) if event.get("goalkeeper") else None,
            "freeze_frame": freeze_frame,
            "timestamp": event.get("timestamp"),
            "related_events": event.get("related_events", []),
        }

    def _load_all_lineups(self, matches: Optional[pd.DataFrame]) -> pd.DataFrame:
        if matches is None or matches.empty:
            return pd.DataFrame()

        match_ids = matches["match_id"].dropna().unique().tolist()
        all_lineups = []

        for mid in match_ids[:50]:
            url = config.STATSBOMB_EVENTS.format(match_id=mid)
            try:
                events_data = requests.get(url, timeout=30).json()
                lineup_events = [e for e in events_data if e.get("type", {}).get("name") == "Starting XI"]
                for le in lineup_events:
                    team = le.get("team", {}).get("name", "")
                    tactics = le.get("tactics", {})
                    formation = tactics.get("formation", "")
                    for player in tactics.get("lineup", []):
                        all_lineups.append({
                            "match_id": mid,
                            "team_name": team,
                            "player_id": player.get("player", {}).get("id"),
                            "player_name": player.get("player", {}).get("name", ""),
                            "jersey_number": player.get("jersey_number"),
                            "position": player.get("position", {}).get("name") if player.get("position") else None,
                            "formation": formation,
                        })
            except Exception as exc:
                self.logger.warning(f"Lineups for match {mid} failed: {exc}")

        return pd.DataFrame(all_lineups)
