
from pathlib import Path
import logging

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text

from db import get_engine


BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)


def create_business_analysis():
    engine = get_engine()

    try:
        query = """
            SELECT
                order_id,
                customer_unique_id,
                order_status,
                order_purchase_timestamp,
                item_revenue,
                payment_total,
                delivery_delay_days,
                avg_review_score
            FROM mart_order_summary
        """

        with engine.connect() as connection:
            df = pd.read_sql(text(query), connection)

        df["order_purchase_timestamp"] = pd.to_datetime(
            df["order_purchase_timestamp"], errors="coerce"
        )

        delivered = df[df["order_status"] == "delivered"].copy()

        if delivered.empty:
            raise ValueError("No delivered orders found for analysis.")

        # North Star metric: monthly delivered GMV, using item prices
        delivered["order_month"] = (
            delivered["order_purchase_timestamp"].dt.to_period("M")
        )

        monthly_gmv = (
            delivered.groupby("order_month")["item_revenue"]
            .sum()
            .reset_index()
        )

        monthly_gmv["order_month"] = (
            monthly_gmv["order_month"].astype(str)
        )

        # Supporting metric 1: monthly delivered orders
        monthly_orders = (
            delivered.groupby("order_month")["order_id"]
            .nunique()
            .reset_index(name="delivered_orders")
        )
        monthly_orders["order_month"] = (
            monthly_orders["order_month"].astype(str)
        )

        # Supporting metric 2: repeat purchase rate
        customer_order_counts = (
            df.dropna(subset=["customer_unique_id"])
            .groupby("customer_unique_id")["order_id"]
            .nunique()
        )

        repeat_rate = (
            (customer_order_counts > 1).sum()
            / len(customer_order_counts) * 100
            if len(customer_order_counts) > 0 else 0
        )

        # Supporting metric 3: average review score
        average_review = delivered["avg_review_score"].mean()

        # Guardrail: late delivery rate among delivered orders
        delay_data = delivered.dropna(subset=["delivery_delay_days"])
        late_rate = (
            (delay_data["delivery_delay_days"] > 0).mean() * 100
            if not delay_data.empty else 0
        )

        # Save metrics
        metrics = pd.DataFrame([
            {
                "metric": "Monthly Delivered GMV",
                "value": (
                    f"{monthly_gmv['item_revenue'].iloc[-1]:.2f}"
                    if not monthly_gmv.empty else "N/A"
                ),
                "definition": "Sum of item prices for delivered orders, by month"
            },
            {
                "metric": "Repeat Purchase Rate",
                "value": f"{repeat_rate:.2f}%",
                "definition": "Unique customers with more than one order / all unique customers"
            },
            {
                "metric": "Average Review Score",
                "value": (
                    f"{average_review:.2f}"
                    if pd.notna(average_review) else "N/A"
                ),
                "definition": "Average review score for delivered orders"
            },
            {
                "metric": "Late Delivery Rate",
                "value": f"{late_rate:.2f}%",
                "definition": "Delivered orders later than estimated / delivered orders with known delay"
            }
        ])

        metrics.to_csv(
            REPORTS_DIR / "business_metrics.csv", index=False
        )

        # Chart 1: Monthly GMV
        plt.figure(figsize=(10, 5))
        plt.plot(
            monthly_gmv["order_month"],
            monthly_gmv["item_revenue"],
            marker="o"
        )
        plt.title("Monthly Delivered GMV")
        plt.xlabel("Month")
        plt.ylabel("GMV (item prices)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "monthly_gmv.png", dpi=150)
        plt.close()

        # Chart 2: Monthly delivered orders
        plt.figure(figsize=(10, 5))
        plt.plot(
            monthly_orders["order_month"],
            monthly_orders["delivered_orders"],
            marker="o"
        )
        plt.title("Monthly Delivered Orders")
        plt.xlabel("Month")
        plt.ylabel("Number of Delivered Orders")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "monthly_orders.png", dpi=150)
        plt.close()

        # Chart 3: Delivery delay vs review score
        plt.figure(figsize=(8, 5))
        plt.scatter(
            delay_data["delivery_delay_days"],
            delay_data["avg_review_score"],
            alpha=0.25
        )
        plt.title("Delivery Delay vs. Review Score")
        plt.xlabel("Delivery Delay (days; positive = late)")
        plt.ylabel("Average Review Score")
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "delivery_vs_review.png", dpi=150)
        plt.close()

        # Chart 4: Delivered order status distribution
        status_counts = df["order_status"].value_counts()
        plt.figure(figsize=(8, 5))
        status_counts.plot(kind="bar")
        plt.title("Order Count by Status")
        plt.xlabel("Order Status")
        plt.ylabel("Number of Orders")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / "order_status.png", dpi=150)
        plt.close()

        logging.info("Business metrics and charts saved in reports/")

    except Exception:
        logging.exception("Business analysis failed.")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    create_business_analysis()
