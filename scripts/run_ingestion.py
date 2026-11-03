"""Run data acquisition and ingestion pipeline."""

from atlas.core.db import init_database
from atlas.sources.fetcher import run_data_acquisition
from atlas.ingestion.pipeline import run_full_ingestion

if __name__ == "__main__":
    print("=" * 60)
    print("  ATLAS DATA PIPELINE REPRODUCIBLE RUNNER")
    print("=" * 60)
    init_database()
    print("\nStep 1: Acquiring official data sources and benchmarks...")
    run_data_acquisition()
    print("\nStep 2: Ingesting into SQLite and DuckDB, creating evidence ledger...")
    res = run_full_ingestion()
    print("\nIngestion pipeline complete:", res)

