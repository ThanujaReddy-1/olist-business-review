
import logging
import pandas as pd

from sqlalchemy import text
from db import get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_staging_tables():
    engine = get_engine()

    try:
        with engine.begin() as connection:

            # Cleaned orders
            connection.execute(text("""
                DROP TABLE IF EXISTS stg_orders;

                CREATE TABLE stg_orders AS
                SELECT
                    NULLIF(order_id, '') AS order_id,
                    NULLIF(customer_id, '') AS customer_id,
                    NULLIF(order_status, '') AS order_status,
                    NULLIF(order_purchase_timestamp, '')::timestamp
                        AS order_purchase_timestamp,
                    NULLIF(order_approved_at, '')::timestamp
                        AS order_approved_at,
                    NULLIF(order_delivered_carrier_date, '')::timestamp
                        AS order_delivered_carrier_date,
                    NULLIF(order_delivered_customer_date, '')::timestamp
                        AS order_delivered_customer_date,
                    NULLIF(order_estimated_delivery_date, '')::timestamp
                        AS order_estimated_delivery_date
                FROM raw_orders;
            """))

            # Cleaned order items
            connection.execute(text("""
                DROP TABLE IF EXISTS stg_order_items;

                CREATE TABLE stg_order_items AS
                SELECT
                    order_id,
                    order_item_id::integer AS order_item_id,
                    product_id,
                    seller_id,
                    NULLIF(shipping_limit_date, '')::timestamp
                        AS shipping_limit_date,
                    NULLIF(price, '')::numeric(12,2) AS price,
                    NULLIF(freight_value, '')::numeric(12,2)
                        AS freight_value
                FROM raw_order_items;
            """))

            # Cleaned payments
            connection.execute(text("""
                DROP TABLE IF EXISTS stg_payments;

                CREATE TABLE stg_payments AS
                SELECT
                    order_id,
                    payment_sequential::integer AS payment_sequential,
                    payment_type,
                    payment_installments::integer AS payment_installments,
                    NULLIF(payment_value, '')::numeric(12,2)
                        AS payment_value
                FROM raw_payments;
            """))

            # Cleaned reviews
            connection.execute(text("""
                DROP TABLE IF EXISTS stg_reviews;

                CREATE TABLE stg_reviews AS
                SELECT
                    review_id,
                    order_id,
                    NULLIF(review_score, '')::integer AS review_score,
                    NULLIF(review_creation_date, '')::timestamp
                        AS review_creation_date,
                    NULLIF(review_answer_timestamp, '')::timestamp
                        AS review_answer_timestamp
                FROM raw_reviews;
            """))

            # Cleaned customers
            connection.execute(text("""
                DROP TABLE IF EXISTS stg_customers;

                CREATE TABLE stg_customers AS
                SELECT
                    customer_id,
                    customer_unique_id,
                    NULLIF(customer_zip_code_prefix, '')::integer
                        AS customer_zip_code_prefix,
                    customer_city,
                    customer_state
                FROM raw_customers;
            """))
            
            # Cleaned products
            connection.execute(text("""
                DROP TABLE IF EXISTS stg_products;
            """))

            connection.execute(text("""
                CREATE TABLE stg_products AS
                SELECT
                    product_id,
                    product_category_name,
                    NULLIF(product_name_lenght, '')::integer
                        AS product_name_lenght,
                    NULLIF(product_description_lenght, '')::integer
                        AS product_description_lenght,
                    NULLIF(product_photos_qty, '')::integer
                        AS product_photos_qty,
                    NULLIF(product_weight_g, '')::numeric
                        AS product_weight_g,
                    NULLIF(product_length_cm, '')::numeric
                        AS product_length_cm,
                    NULLIF(product_height_cm, '')::numeric
                        AS product_height_cm,
                    NULLIF(product_width_cm, '')::numeric
                        AS product_width_cm
                FROM raw_products;
            """))

        logging.info("Staging tables created successfully.")

    except Exception:
        logging.exception("Staging table creation failed.")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    create_staging_tables()
