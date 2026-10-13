
from pathlib import Path
import logging
import pandas as pd

from db import get_engine

# Find the main project folder and the data folder
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Map each CSV file to its raw database table
FILES = {
    "olist_orders_dataset.csv": "raw_orders",
    "olist_order_items_dataset.csv": "raw_order_items",
    "olist_order_payments_dataset.csv": "raw_payments",
    "olist_order_reviews_dataset.csv": "raw_reviews",
    "olist_customers_dataset.csv": "raw_customers",
    "olist_products_dataset.csv": "raw_products",
    "olist_sellers_dataset.csv": "raw_sellers",
    "olist_geolocation_dataset.csv": "raw_geolocation",
}

# Columns expected in each required CSV file
EXPECTED_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
    "olist_order_payments_dataset.csv": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ],
    "olist_customers_dataset.csv": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
    "olist_products_dataset.csv": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
    "olist_sellers_dataset.csv": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ],
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def validate_files():
    """Check that all required files and columns exist."""

    validated_files = {}

    for filename, table_name in FILES.items():
        file_path = DATA_DIR / filename

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Required CSV file is missing: {file_path}"
            )

        # Read only the header first
        actual_columns = pd.read_csv(
            file_path,
            nrows=0,
        ).columns.tolist()

        expected = set(EXPECTED_COLUMNS[filename])
        actual = set(actual_columns)

        missing_columns = expected - actual

        if missing_columns:
            raise ValueError(
                f"{filename} is missing columns: "
                f"{sorted(missing_columns)}"
            )

        validated_files[filename] = (file_path, table_name)

        logging.info("Validated file: %s", filename)

    return validated_files


def load_raw_tables():
    """Load the CSV files into raw PostgreSQL tables."""

    # Validate every required file before loading anything
    validated_files = validate_files()

    engine = get_engine()

    try:
        # A transaction helps prevent a partially replaced dataset
        # if a loading step fails.
        with engine.begin() as connection:

            for filename, (file_path, table_name) in (
                validated_files.items()
            ):
                logging.info("Loading %s", filename)

                # Preserve identifiers and original text in raw tables
                df = pd.read_csv(
                    file_path,
                    dtype=str,
                    keep_default_na=False,
                )

                # Replace the previous snapshot instead of appending
                df.to_sql(
                    name=table_name,
                    con=connection,
                    if_exists="replace",
                    index=False,
                    chunksize=10000,
                )

                logging.info(
                    "Loaded %s rows into %s",
                    len(df),
                    table_name,
                )

        logging.info("All raw tables loaded successfully.")

    except Exception:
        logging.exception("Raw ingestion failed.")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_raw_tables()
