
import logging
import pandas as pd
from sqlalchemy import text
from db import get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


CHECKS = {
    "Missing order IDs": """
        SELECT COUNT(*)
        FROM stg_orders
        WHERE order_id IS NULL OR TRIM(order_id) = ''
    """,

    "Duplicate order IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM stg_orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Invalid review scores": """
        SELECT COUNT(*)
        FROM stg_reviews
        WHERE review_score IS NOT NULL
          AND review_score NOT BETWEEN 1 AND 5
    """,

    "Negative item prices": """
        SELECT COUNT(*)
        FROM stg_order_items
        WHERE price < 0
    """,

    "Orders with missing customers": """
        SELECT COUNT(*)
        FROM stg_orders o
        LEFT JOIN stg_customers c
            ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """,

    "Delivery before purchase": """
        SELECT COUNT(*)
        FROM stg_orders
        WHERE order_delivered_customer_date
              < order_purchase_timestamp
    """,
}


def run_quality_checks():
    engine = get_engine()
    results = []

    try:
        with engine.connect() as connection:
            for check_name, query in CHECKS.items():
                failed_rows = connection.execute(
                    text(query)
                ).scalar_one()

                status = "PASS" if failed_rows == 0 else "FAIL"

                results.append({
                    "check_name": check_name,
                    "failed_rows": failed_rows,
                    "status": status,
                })

                logging.info(
                    "%s | Failed rows: %s | Status: %s",
                    check_name,
                    failed_rows,
                    status,
                )

        report = pd.DataFrame(results)
        report.to_csv(
            "quality_check_results.csv",
            index=False
        )

        if any(row["status"] == "FAIL" for row in results):
            raise ValueError(
                "Data-quality checks failed. Review "
                "quality_check_results.csv before proceeding."
            )

        logging.info("All data-quality checks passed.")

    except Exception:
        logging.exception("Quality checks encountered a failure.")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    run_quality_checks()
