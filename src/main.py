
import logging

from ingest import load_raw_tables
from transform import create_staging_tables
from quality_checks import run_quality_checks
from create_mart import create_order_mart


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_pipeline():
    try:
        logging.info("Starting the e-commerce data pipeline.")

        logging.info("Step 1: Loading raw CSV data.")
        load_raw_tables()

        logging.info("Step 2: Creating staging tables.")
        create_staging_tables()

        logging.info("Step 3: Running data-quality checks.")
        run_quality_checks()

        logging.info("Step 4: Creating the order mart.")
        create_order_mart()

        logging.info("Pipeline completed successfully.")

    except Exception:
        logging.exception("Pipeline failed.")
        raise


if __name__ == "__main__":
    run_pipeline()
