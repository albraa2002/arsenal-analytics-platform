"""
FBref extractor — scrapes squad stats for the Premier League using multi-index
HTML tables. Covers standard stats, shooting, passing, possession, defence,
goalkeeping, passing types, progressive passing, and pressing.
"""

import re
from typing import Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup

from config.config import config
from scripts.extraction.base_extractor import BaseExtractor


class FBrefExtractor(BaseExtractor):
    """Scrapes per-game and per-90 stats tables from FBref."""

    TABLE_IDS: List[str] = [
        "stats_standard",
        "stats_shooting",
        "stats_passing",
        "stats_passing_types",
        "stats_gca",
        "stats_defense",
        "stats_possession",
        "stats_misc",
        "keepers",
        "keepers_adv",
    ]

    # Additional progressive passing / pressing tables available via same pattern
    PROGRESSIVE_TABLE_IDS: List[str] = [
        "stats_passing",
    ]

    def __init__(self):
        super().__init__("fbref")

    def extract(self, **kwargs) -> Dict[str, pd.DataFrame]:
        season: str = kwargs.get("season", config.CURRENT_SEASON)
        tables: Dict[str, pd.DataFrame] = {}
        for table_id in self.TABLE_IDS:
            try:
                df = self._scrape_table(table_id, season)
                if df is not None and not df.empty:
                    tables[table_id] = df
                    self.save_dataframe(df, f"epl_{table_id}_{season.replace('-', '_')}")
                    self.logger.info(f"Extracted {table_id}: {len(df)} rows")
            except Exception as exc:
                self.logger.error(f"Failed to scrape {table_id}: {exc}")
        return tables

    def _scrape_table(self, table_id: str, season: str) -> Optional[pd.DataFrame]:
        url = f"{config.FBREF_BASE}/{season.replace('-', '')}/stats/{season.replace('-', '')}-Premier-League-Stats"
        soup = self._request_soup(url)

        table = soup.find("table", {"id": table_id})
        if not table:
            self.logger.warning(f"Table #{table_id} not found on page")
            return None

        rows = table.find_all("tr")
        headers = self._parse_headers(table)
        data = []
        for row in rows:
            cells = row.find_all(["th", "td"])
            vals = [cell.get_text(strip=True) for cell in cells]
            if len(vals) == len(headers):
                data.append(vals)

        if not data:
            return None

        df = pd.DataFrame(data, columns=headers)

        numeric_cols = [c for c in df.columns if c not in ("player", "pos", "team", "nation")]
        for col in numeric_cols:
            df[col] = (
                df[col]
                .str.replace(",", "", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
            )

        df["season"] = season
        df["source"] = "fbref"
        return df

    def _parse_headers(self, table) -> List[str]:
        header_rows = table.find_all("tr")
        cols: List[str] = []
        for th in header_rows:
            cols_this_row = []
            for cell in th.find_all(["th", "td"]):
                colspan = int(cell.get("colspan", 1))
                text = cell.get_text(strip=True).lower().replace(" ", "_")
                for _ in range(colspan):
                    cols_this_row.append(text)
            if cols_this_row:
                cols = cols_this_row
        return cols

    def extract_player_stats(self, player_url: str) -> Optional[pd.DataFrame]:
        soup = self._request_soup(player_url)
        table = soup.find("table", {"id": "stats_standard_9"})
        if not table:
            return None
        return self._parse_table_to_df(table)

    def _parse_table_to_df(self, table) -> pd.DataFrame:
        rows = table.find_all("tr")
        headers = self._parse_headers(table)
        data = []
        for row in rows:
            cells = row.find_all(["th", "td"])
            vals = [cell.get_text(strip=True) for cell in cells]
            if len(vals) == len(headers):
                data.append(vals)
        return pd.DataFrame(data, columns=headers) if data else pd.DataFrame()

    def extract_squad_data(self, squad_url: str) -> Optional[pd.DataFrame]:
        soup = self._request_soup(squad_url)
        table = soup.find("table", {"id": "stats_standard_9"})
        if not table:
            return None
        return self._parse_table_to_df(table)
