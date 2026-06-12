"""
Phase 3 — Entity Resolution

Robust player matching across sources using rapidfuzz, difflib,
and a curated alias dictionary. Handles name mismatches, accents,
short names, and common nicknames.
"""

import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
from rapidfuzz import fuzz, process

from config.logging_config import get_logger


class EntityResolver:
    """Matches player names across data sources with fuzzy logic."""

    # Curated alias dictionary: canonical → list of known variants
    PLAYER_ALIASES: Dict[str, List[str]] = {
        "Bukayo Saka": ["Saka", "Bukayo Saka"],
        "Martin Odegaard": ["Odegaard", "Martin Odegaard", "Martin Ødegaard", "Ødegaard"],
        "Gabriel Jesus": ["Gabriel Jesus", "Jesus", "G. Jesus"],
        "Gabriel Martinelli": ["Martinelli", "Gabriel Martinelli", "G. Martinelli"],
        "Gabriel Magalhaes": ["Gabriel", "Gabriel Magalhães", "Gabriel Magalhaes"],
        "William Saliba": ["Saliba", "William Saliba"],
        "Ben White": ["Ben White", "B. White"],
        "Thomas Partey": ["Partey", "Thomas Partey"],
        "Declan Rice": ["Rice", "Declan Rice"],
        "Kai Havertz": ["Havertz", "Kai Havertz"],
        "Leandro Trossard": ["Trossard", "Leandro Trossard"],
        "Jurrien Timber": ["Timber", "Jurrien Timber"],
        "Jakub Kiwior": ["Kiwior", "Jakub Kiwior"],
        "Takehiro Tomiyasu": ["Tomiyasu", "Takehiro Tomiyasu"],
        "Oleksandr Zinchenko": ["Zinchenko", "Oleksandr Zinchenko"],
        "Jorginho": ["Jorginho"],
        "Mohamed Elneny": ["Elneny", "Mohamed Elneny"],
        "Emile Smith Rowe": ["Smith Rowe", "Emile Smith Rowe", "E. Smith Rowe"],
        "Reiss Nelson": ["Nelson", "Reiss Nelson"],
        "Eddie Nketiah": ["Nketiah", "Eddie Nketiah"],
        "Fabio Vieira": ["Vieira", "Fábio Vieira", "Fabio Vieira"],
        "Aaron Ramsdale": ["Ramsdale", "Aaron Ramsdale"],
        "David Raya": ["Raya", "David Raya"],
        "Matt Turner": ["Turner", "Matt Turner"],
        "Cedric Soares": ["Cédric", "Cedric", "Cedric Soares"],
        "Nuno Tavares": ["Tavares", "Nuno Tavares", "N. Tavares"],
        "Marquinhos": ["Marquinhos"],
        "Albert Sambi Lokonga": ["Lokonga", "Sambi Lokonga", "Albert Sambi Lokonga"],
        "Nicolas Pepe": ["Pépé", "Pepe", "Nicolas Pepe"],
        "Alexandre Lacazette": ["Lacazette", "Alexandre Lacazette"],
        "Pierre-Emerick Aubameyang": ["Aubameyang", "P. Aubameyang", "Pierre-Emerick Aubameyang"],
        "Granit Xhaka": ["Xhaka", "Granit Xhaka"],
        "Kieran Tierney": ["Tierney", "Kieran Tierney"],
        "Rob Holding": ["Holding", "Rob Holding"],
        "Pablo Mari": ["Mari", "Pablo Marí", "Pablo Mari"],
        "Calum Chambers": ["Chambers", "Calum Chambers"],
        "Ainsley Maitland-Niles": ["Maitland-Niles", "Ainsley Maitland-Niles"],
        "Hector Bellerin": ["Bellerín", "Bellerin", "Hector Bellerin"],
        "Bernd Leno": ["Leno", "Bernd Leno"],
        "Mikel Arteta": ["Arteta", "Mikel Arteta"],
        "Ethan Nwaneri": ["Nwaneri", "Ethan Nwaneri"],
        "Myles Lewis-Skelly": ["Lewis-Skelly", "Myles Lewis-Skelly"],
        "Riccardo Calafiori": ["Calafiori", "Riccardo Calafiori"],
    }

    def __init__(self, threshold: int = 85, logger_name: str = "entity_resolver"):
        self.threshold = threshold
        self.logger = get_logger(logger_name)
        self._canonical_map: Dict[str, str] = {}
        self._build_canonical_map()

        # All known aliases (lowercased) for quick lookup
        self._alias_set: Set[str] = set()
        for canon, aliases in self.PLAYER_ALIASES.items():
            for alias in aliases:
                self._alias_set.add(alias.lower())

    def _build_canonical_map(self):
        for canon, aliases in self.PLAYER_ALIASES.items():
            for alias in aliases:
                self._canonical_map[alias.lower()] = canon

    def resolve(self, name: str) -> str:
        """Resolve a raw name to a canonical player name."""
        cleaned = self._clean(name)
        if not cleaned:
            return name

        # Direct hit
        if cleaned.lower() in self._canonical_map:
            return self._canonical_map[cleaned.lower()]

        # Fuzzy match against all known aliases
        best_match, score, _ = process.extractOne(
            cleaned, self._alias_set, scorer=fuzz.WRatio, score_cutoff=self.threshold
        )
        if best_match and score >= self.threshold:
            return self._canonical_map.get(best_match, cleaned)

        # Fuzzy match against canonical names directly
        canonical_names = list(self.PLAYER_ALIASES.keys())
        best_canon, score2, _ = process.extractOne(
            cleaned, canonical_names, scorer=fuzz.WRatio, score_cutoff=self.threshold
        )
        if best_canon and score2 >= self.threshold:
            return best_canon

        return cleaned

    def resolve_dataframe(
        self, df: pd.DataFrame, name_column: str = "player_name"
    ) -> pd.DataFrame:
        df = df.copy()
        df["resolved_name"] = df[name_column].apply(self.resolve)
        unresolved = df[df["resolved_name"] != df[name_column]]
        if not unresolved.empty:
            self.logger.info(
                f"Resolved {len(df) - len(unresolved)}/{len(df)} names "
                f"({len(unresolved)} unmatched)"
            )
            for name in unresolved[name_column].unique():
                self.logger.debug(f"  Unmatched: '{name}'")
        return df

    def merge_players(
        self,
        primary_df: pd.DataFrame,
        secondary_df: pd.DataFrame,
        on: str = "player_name",
        how: str = "left",
    ) -> pd.DataFrame:
        primary_df = self.resolve_dataframe(primary_df, on)
        secondary_df = self.resolve_dataframe(secondary_df, on)

        return primary_df.merge(
            secondary_df,
            left_on="resolved_name",
            right_on="resolved_name",
            how=how,
            suffixes=("", "_other"),
        )

    def _clean(self, name: str) -> str:
        if pd.isna(name) or not isinstance(name, str):
            return ""
        name = name.strip()
        # Unicode normalisation
        name = unicodedata.normalize("NFKD", name)
        name = name.encode("ascii", "ignore").decode("ascii")
        # Remove common suffixes
        name = re.sub(r"\s*(Jr\.?|Sr\.?|II|III|IV)\s*$", "", name, flags=re.IGNORECASE)
        # Collapse whitespace
        name = re.sub(r"\s+", " ", name).strip()
        return name

    def build_entity_table(self, sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Build a unified player entity table from multiple source dataframes."""
        records = []
        seen = set()

        for source_name, df in sources.items():
            name_col = "player_name"
            if name_col not in df.columns:
                continue

            for name in df[name_col].dropna().unique():
                canonical = self.resolve(name)
                if canonical not in seen:
                    seen.add(canonical)
                    source_type = source_name.split("_")[0]
                    records.append({
                        "canonical_name": canonical,
                        "source_name": name,
                        "primary_source": source_type,
                    })

        entity_df = pd.DataFrame(records)
        self.logger.info(f"Built entity table with {len(entity_df)} unique players")
        return entity_df
