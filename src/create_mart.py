
import logging
from sqlalchemy import text
from db import get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_order_mart():
    engine = get_engine()

    try:
        with engine.begin() as connection:
            connection.execute(text("""
                DROP TABLE IF EXISTS mart_order_summary;
            """))

            connection.execute(text("""
                CREATE TABLE mart_order_summary AS
                WITH item_totals AS (
                    SELECT
                        order_id,
                        SUM(price) AS item_revenue,
                        SUM(freight_value) AS freight_total
                    FROM stg_order_items
                    GROUP BY order_id
                ),
                payment_totals AS (
                    SELECT
                        order_id,
                        SUM(payment_value) AS payment_total
                    FROM stg_payments
                    GROUP BY order_id
                ),
                review_totals AS (
                    SELECT
                        order_id,
                        AVG(review_score) AS avg_review_score
                    FROM stg_reviews
                    GROUP BY order_id
                )
                SELECT
                    o.order_id,
                    o.customer_id,
                    c.customer_unique_id,
                    c.customer_state,
                    o.order_status,
                    o.order_purchase_timestamp,
                    o.order_delivered_customer_date,
                    o.order_estimated_delivery_date,
                    COALESCE(i.item_revenue, 0) AS item_revenue,
                    COALESCE(i.freight_total, 0) AS freight_total,
                    COALESCE(p.payment_total, 0) AS payment_total,
                    r.avg_review_score,
                    CASE
                        WHEN o.order_delivered_customer_date IS NOT NULL
                         AND o.order_estimated_delivery_date IS NOT NULL
                        THEN
                            EXTRACT(
                                EPOCH FROM (
                                    o.order_delivered_customer_date
                                    - o.order_estimated_delivery_date
                                )
                            ) / 86400.0
                    END AS delivery_delay_days
                FROM stg_orders o
                LEFT JOIN stg_customers c
                    ON o.customer_id = c.customer_id
                LEFT JOIN item_totals i
                    ON o.order_id = i.order_id
                LEFT JOIN payment_totals p
                    ON o.order_id = p.order_id
                LEFT JOIN review_totals r
                    ON o.order_id = r.order_id;
            """))

        logging.info("Order mart created successfully.")

    except Exception:
        logging.exception("Order mart creation failed.")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    create_order_mart()
