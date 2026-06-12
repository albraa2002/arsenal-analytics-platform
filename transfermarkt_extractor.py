"""
Transfermarkt extractor — scrapes squad values, transfers, injuries,
and contract expiry data from Transfermarkt.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup

from config.config import config
from scripts.extraction.base_extractor import BaseExtractor


class TransfermarktExtractor(BaseExtractor):
    """Scrapes Transfermarkt pages for values, injuries, and contract data."""

    ARSENAL_TRANSFERMARKT_ID: str = "11"
    BASE_TEAM_URL: str = "https://www.transfermarkt.com/arsenal-fc/startseite/verein/{sid}/plus/0?reldata={season}"

    def __init__(self):
        super().__init__("transfermarkt", cache_ttl=7200)

    def extract(self, **kwargs) -> Dict[str, pd.DataFrame]:
        results: Dict[str, pd.DataFrame] = {}

        try:
            results["squad"] = self._scrape_squad()
            if not results["squad"].empty:
                self.save_dataframe(results["squad"], "transfermarkt_squad")
        except Exception as exc:
            self.logger.error(f"Squad scrape failed: {exc}")

        try:
            results["injuries"] = self._scrape_injuries()
            if not results["injuries"].empty:
                self.save_dataframe(results["injuries"], "transfermarkt_injuries")
        except Exception as exc:
            self.logger.error(f"Injuries scrape failed: {exc}")

        try:
            results["transfers"] = self._scrape_transfers()
            if not results["transfers"].empty:
                self.save_dataframe(results["transfers"], "transfermarkt_transfers")
        except Exception as exc:
            self.logger.error(f"Transfers scrape failed: {exc}")

        return results

    def _scrape_squad(self) -> pd.DataFrame:
        season_param = config.CURRENT_SEASON.replace("-", "")
        url = self.BASE_TEAM_URL.format(
            sid=self.ARSENAL_TRANSFERMARKT_ID,
            season=season_param
        )
        soup = self._request_soup(url)
        rows = []

        table = soup.find("table", {"class": "items"})
        if not table:
            self.logger.warning("Squad table not found")
            return pd.DataFrame()

        for row in table.find_all("tr", {"class": ["odd", "even"]}):
            cells = row.find_all("td")
            if len(cells) < 10:
                continue

            name_tag = row.find("td", {"class": "hauptlink"})
            name = name_tag.get_text(strip=True) if name_tag else ""

            pos_tag = cells[1] if len(cells) > 1 else None
            position = pos_tag.get_text(strip=True) if pos_tag else ""

            age_tag = cells[2] if len(cells) > 2 else None
            age = age_tag.get_text(strip=True) if age_tag else ""

            nat_tag = cells[3].find("img") if len(cells) > 3 else None
            nationality = nat_tag.get("alt", "") if nat_tag else ""

            market_val_tag = cells[7] if len(cells) > 7 else None
            market_value = self._parse_market_value(
                market_val_tag.get_text(strip=True) if market_val_tag else "0"
            )

            contract_tag = cells[5] if len(cells) > 5 else None
            contract_until = contract_tag.get_text(strip=True) if contract_tag else ""

            rows.append({
                "player_name": name,
                "position": position,
                "age": age,
                "nationality": nationality,
                "market_value_euro": market_value,
                "contract_until": contract_until,
                "season": config.CURRENT_SEASON,
            })

        return pd.DataFrame(rows)

    def _scrape_injuries(self) -> pd.DataFrame:
        url = f"https://www.transfermarkt.com/arsenal-fc/verletzungen/verein/{self.ARSENAL_TRANSFERMARKT_ID}"
        soup = self._request_soup(url)
        rows = []

        table = soup.find("table", {"class": "items"})
        if not table:
            return pd.DataFrame()

        for row in table.find_all("tr", {"class": ["odd", "even"]}):
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            name_tag = cells[0].find("a")
            name = name_tag.get_text(strip=True) if name_tag else ""
            injury_tag = cells[1]
            injury = injury_tag.get_text(strip=True) if injury_tag else ""
            until_tag = cells[2]
            until = until_tag.get_text(strip=True) if until_tag else ""

            rows.append({
                "player_name": name,
                "injury": injury,
                "return_date": until,
                "season": config.CURRENT_SEASON,
            })

        return pd.DataFrame(rows)

    def _scrape_transfers(self) -> pd.DataFrame:
        url = f"https://www.transfermarkt.com/arsenal-fc/transfers/verein/{self.ARSENAL_TRANSFERMARKT_ID}/plus/0"
        soup = self._request_soup(url)
        rows = []

        for table in soup.find_all("table", {"class": "items"}):
            is_arrivals = "arrivals" in str(table.get("id", "")) or True
            for row in table.find_all("tr", {"class": ["odd", "even"]}):
                cells = row.find_all("td")
                if len(cells) < 5:
                    continue
                name_tag = cells[0].find("a")
                name = name_tag.get_text(strip=True) if name_tag else ""
                pos_tag = cells[1]
                position = pos_tag.get_text(strip=True) if pos_tag else ""
                from_to_tag = cells[2]
                from_to = from_to_tag.get_text(strip=True) if from_to_tag else ""
                fee_tag = cells[3]
                fee = self._parse_market_value(
                    fee_tag.get_text(strip=True) if fee_tag else "0"
                )

                rows.append({
                    "player_name": name,
                    "position": position,
                    "from_to_club": from_to,
                    "transfer_fee_euro": fee,
                    "type": "arrival" if is_arrivals else "departure",
                    "season": config.CURRENT_SEASON,
                })

        return pd.DataFrame(rows)

    def _parse_market_value(self, val_str: str) -> float:
        val_str = val_str.strip()
        if not val_str or val_str in ("-", ""):
            return 0.0
        mult = 1.0
        if "m" in val_str:
            mult = 1_000_000
        elif "k" in val_str or "Tsd" in val_str:
            mult = 1_000
        val_str = val_str.replace("€", "").replace("m", "").replace("k", "").replace("Tsd.", "").strip()
        try:
            return float(val_str.replace(",", ".")) * mult
        except ValueError:
            return 0.0
