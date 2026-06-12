"""
Orchestrator — runs all extraction pipelines and collects results.
"""

import sys
from pathlib import Path
from typing import Dict

import pandas as pd

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config.config import config
from config.logging_config import setup_logging
from scripts.extraction.fbref_extractor import FBrefExtractor
from scripts.extraction.understat_extractor import UnderstatExtractor
from scripts.extraction.fpl_extractor import FPLExtractor
from scripts.extraction.statsbomb_extractor import StatsBombExtractor
from scripts.extraction.fotmob_extractor import FotmobExtractor
from scripts.extraction.transfermarkt_extractor import TransfermarktExtractor


def run_all_extractions() -> Dict[str, pd.DataFrame]:
    logger = setup_logging("extraction_pipeline", log_file="outputs/reports/extraction.log")
    all_data: Dict[str, pd.DataFrame] = {}

    extractors = [
        ("fbref", FBrefExtractor()),
        ("understat", UnderstatExtractor()),
        ("fpl", FPLExtractor()),
        ("statsbomb", StatsBombExtractor()),
        ("fotmob", FotmobExtractor()),
        ("transfermarkt", TransfermarktExtractor()),
    ]

    for source_name, extractor in extractors:
        logger.info(f"=== Starting {source_name} extraction ===")
        try:
            result = extractor.run()
            for table_key, df in result.items():
                compound_key = f"{source_name}_{table_key}"
                all_data[compound_key] = df
                logger.info(f"  → {compound_key}: {len(df)} rows")
        except Exception as exc:
            logger.error(f"{source_name} extraction failed: {exc}", exc_info=True)

    logger.info(f"Extraction complete. Total datasets: {len(all_data)}")
    return all_data


if __name__ == "__main__":
    data = run_all_extractions()
    print(f"\nExtracted {len(data)} datasets:")
    for name, df in data.items():
        print(f"  {name}: {df.shape}")
