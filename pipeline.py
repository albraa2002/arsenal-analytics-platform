"""
Main pipeline orchestrator — runs the entire Arsenal analytics platform
end-to-end: extraction → cleaning → resolution → warehouse → features → modeling → viz → export.
"""

import sys
from pathlib import Path
from typing import Dict

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.config import config
from config.logging_config import setup_logging

from scripts.extraction.extract_all import run_all_extractions
from scripts.preprocessing.cleaner import DataCleaner
from scripts.preprocessing.normalizer import ColumnNormalizer
from scripts.integration.entity_resolver import EntityResolver
from scripts.feature_engineering.team_metrics import TeamMetricsEngine
from scripts.feature_engineering.player_metrics import PlayerMetricsEngine
from scripts.feature_engineering.tactical_metrics import TacticalMetricsEngine
from scripts.modeling.match_predictor import MatchPredictor
from scripts.modeling.player_performance import PlayerPerformancePredictor
from scripts.modeling.injury_risk import InjuryRiskEstimator
from scripts.modeling.fpl_forecaster import FPLForecaster
from scripts.integration.powerbi_export import PowerBIExporter


class ArsenalAnalyticsPipeline:
    """End-to-end pipeline builder for the Arsenal analytics platform."""

    def __init__(self):
        self.logger = setup_logging(
            "arsenal_pipeline",
            log_file=str(config.paths.reports / "pipeline.log"),
        )
        self.cleaner = DataCleaner()
        self.normalizer = ColumnNormalizer()
        self.resolver = EntityResolver()
        self.pbi_exporter = PowerBIExporter()

        self.raw_data: Dict[str, pd.DataFrame] = {}
        self.clean_data: Dict[str, pd.DataFrame] = {}
        self.resolved_data: Dict[str, pd.DataFrame] = {}

    def run_phase_1_extraction(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("=" * 60)
        self.logger.info("PHASE 1: DATA EXTRACTION")
        self.logger.info("=" * 60)

        self.raw_data = run_all_extractions()
        self.logger.info(f"Extraction complete: {len(self.raw_data)} datasets")
        return self.raw_data

    def run_phase_2_cleaning(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("=" * 60)
        self.logger.info("PHASE 2: DATA CLEANING & NORMALIZATION")
        self.logger.info("=" * 60)

        self.clean_data = {}
        for source_name, df in self.raw_data.items():
            try:
                df_norm = self.normalizer.normalize(df, source_name)
                df_clean = self.cleaner.clean(df_norm, source_name)
                self.clean_data[source_name] = df_clean
                self.logger.info(f"Cleaned {source_name}: {len(df_clean)} rows")
            except Exception as exc:
                self.logger.error(f"Cleaning failed for {source_name}: {exc}")

        return self.clean_data

    def run_phase_3_entity_resolution(self) -> Dict[str, pd.DataFrame]:
        self.logger.info("=" * 60)
        self.logger.info("PHASE 3: ENTITY RESOLUTION")
        self.logger.info("=" * 60)

        for source_name, df in self.clean_data.items():
            if "player_name" in df.columns:
                try:
                    self.resolved_data[source_name] = self.resolver.resolve_dataframe(df)
                except Exception as exc:
                    self.logger.error(f"Resolution failed for {source_name}: {exc}")
                    self.resolved_data[source_name] = df
            else:
                self.resolved_data[source_name] = df

        entity_table = self.resolver.build_entity_table(self.resolved_data)
        self.pbi_exporter.export_to_csv({"dim_players": entity_table})

        return self.resolved_data

    def run_phase_4_warehouse(self):
        self.logger.info("=" * 60)
        self.logger.info("PHASE 4: DATA WAREHOUSE")
        self.logger.info("=" * 60)

        from database.setup import setup_database
        db = setup_database()

        # Export resolved data to star schema tables
        star_data = {}
        for source_name, df in self.resolved_data.items():
            safe_name = source_name.replace("-", "_").lower()[:60]
            star_data[safe_name] = df

        self.pbi_exporter.export_star_schema(star_data)
        db.dispose()
        self.logger.info("Star schema created and populated")

    def run_phase_5_feature_engineering(self):
        self.logger.info("=" * 60)
        self.logger.info("PHASE 5: FEATURE ENGINEERING")
        self.logger.info("=" * 60)

        team_engine = TeamMetricsEngine()
        player_engine = PlayerMetricsEngine()
        tactical_engine = TacticalMetricsEngine()

        for source_name, df in self.resolved_data.items():
            try:
                if "team_name" in df.columns and "xG" in df.columns:
                    player_features = player_engine.compute_all(df)
                    out_path = config.paths.features / f"{source_name}_player_features.parquet"
                    player_features.to_parquet(out_path)

                if "location_x" in df.columns and "location_y" in df.columns:
                    avg_pos = tactical_engine.compute_average_positions(df)
                    out_path = config.paths.features / f"{source_name}_avg_positions.parquet"
                    avg_pos.to_parquet(out_path)

            except Exception as exc:
                self.logger.debug(f"Feature engineering skipped for {source_name}: {exc}")

        self.logger.info("Feature engineering complete")

    def run_phase_6_modeling(self):
        self.logger.info("=" * 60)
        self.logger.info("PHASE 6: MACHINE LEARNING")
        self.logger.info("=" * 60)

        match_predictor = MatchPredictor()
        fpl_forecaster = FPLForecaster()

        for source_name, df in self.resolved_data.items():
            if "home_xG" in df.columns and "result" in df.columns:
                try:
                    match_predictor.train(df)
                except Exception as exc:
                    self.logger.warning(f"Match prediction failed for {source_name}: {exc}")

            if "total_points" in df.columns and "gameweek" in df.columns:
                try:
                    fpl_forecaster.train(df)
                except Exception as exc:
                    self.logger.warning(f"FPL forecasting failed for {source_name}: {exc}")

        match_predictor.save_models()
        fpl_forecaster.save_models()

    def run_phase_7_visualization(self):
        self.logger.info("=" * 60)
        self.logger.info("PHASE 7: VISUALIZATION")
        self.logger.info("=" * 60)

        from scripts.visualization.pitch_plots import PitchPlotter
        from scripts.visualization.analysis_plots import AnalysisPlotter

        pitch_viz = PitchPlotter()
        analysis_viz = AnalysisPlotter()

        for source_name, df in self.resolved_data.items():
            if "location_x" in df.columns and "location_y" in df.columns:
                try:
                    if "statsbomb_xg" in df.columns:
                        pitch_viz.plot_shot_map(
                            df, title=f"Shot Map — {source_name}",
                            save_path=f"{source_name}_shot_map.png",
                        )
                    if "end_location_x" in df.columns and "pass_recipient" in df.columns:
                        pitch_viz.plot_pass_map(
                            df.head(200), title=f"Pass Map — {source_name}",
                            save_path=f"{source_name}_pass_map.png",
                        )
                except Exception as exc:
                    self.logger.debug(f"Plotting failed for {source_name}: {exc}")

        self.logger.info("Visualization complete")

    def run_phase_8_powerbi_export(self):
        self.logger.info("=" * 60)
        self.logger.info("PHASE 8: POWER BI EXPORT")
        self.logger.info("=" * 60)

        csv_data = {}
        sqlite_data = {}
        star_data = {}

        for source_name, df in self.clean_data.items():
            clean_name = source_name.replace("-", "_").lower()[:60]
            csv_data[clean_name] = df

        # Create Power BI-specific view datasets
        for source_name, df in self.resolved_data.items():
            clean_name = f"resolved_{source_name}".replace("-", "_").lower()[:60]
            sqlite_data[clean_name] = df

        for source_name, df in self.raw_data.items():
            clean_name = f"raw_{source_name}".replace("-", "_").lower()[:60]
            star_data[clean_name] = df

        self.pbi_exporter.export_all(csv_data, sqlite_data, star_data)

    def run_full_pipeline(self):
        self.logger.info("🚀 Starting Arsenal Analytics Pipeline")
        self.logger.info(f"Season: {config.CURRENT_SEASON}")

        self.run_phase_1_extraction()
        self.run_phase_2_cleaning()
        self.run_phase_3_entity_resolution()
        self.run_phase_4_warehouse()
        self.run_phase_5_feature_engineering()
        self.run_phase_6_modeling()
        self.run_phase_7_visualization()
        self.run_phase_8_powerbi_export()

        self.logger.info("=" * 60)
        self.logger.info("ARSENAL ANALYTICS PIPELINE COMPLETE")
        self.logger.info("=" * 60)
        self.logger.info(f"All outputs in {config.paths.root}")
        self.logger.info(f"Power BI data in {config.paths.final}")
        self.logger.info(f"Database in {config.paths.database}")
        self.logger.info(f"Plots in {config.paths.plots}")
        self.logger.info(f"Models in {config.paths.models}")

        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Arsenal Analytics Pipeline")
    parser.add_argument(
        "--phase", type=int, choices=range(1, 9), default=0,
        help="Run a specific phase only (1-8). Default: full pipeline.",
    )
    args = parser.parse_args()

    pipeline = ArsenalAnalyticsPipeline()
    phase_map = {
        1: pipeline.run_phase_1_extraction,
        2: pipeline.run_phase_2_cleaning,
        3: pipeline.run_phase_3_entity_resolution,
        4: pipeline.run_phase_4_warehouse,
        5: pipeline.run_phase_5_feature_engineering,
        6: pipeline.run_phase_6_modeling,
        7: pipeline.run_phase_7_visualization,
        8: pipeline.run_phase_8_powerbi_export,
    }

    if args.phase:
        phase_map[args.phase]()
        print(f"Phase {args.phase} complete.")
    else:
        pipeline.run_full_pipeline()
