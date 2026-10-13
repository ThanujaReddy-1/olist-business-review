# Olist E-commerce Weekly Business Review

## Project Overview

This project builds a repeatable ELT pipeline using the Olist Brazilian e-commerce dataset. It loads raw CSV files into PostgreSQL, creates cleaned staging tables, runs data-quality checks, builds an analysis-ready order mart, and generates business metrics and charts.

## Technology Stack

- Python
- PostgreSQL
- SQL and window functions
- Pandas
- SQLAlchemy
- Matplotlib
- python-dotenv

## Project Structure

```text
olist-business-review/
├── data/                  # Source CSV files (not committed)
├── src/
│   ├── db.py
│   ├── ingest.py
│   ├── transform.py
│   ├── quality_checks.py
│   ├── create_mart.py
│   ├── business_analysis.py
│   └── main.py
├── sql/
│   └── analysis_queries.sql
├── reports/
│   ├── business_metrics.csv
│   ├── monthly_gmv.png
│   ├── monthly_orders.png
│   ├── delivery_vs_review.png
│   ├── order_status.png
│   └── vp_memo.md
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. Install Python and PostgreSQL.
2. Create a PostgreSQL database named `olist_db`.
3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate it on Windows:

   ```bash
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Configure database connection variables in `.env`.
7. Place the required Olist CSV files in the `data/` directory.

## Run the Pipeline

From the project root, execute:

```bash
python src/main.py
```

The pipeline loads the raw tables, creates staging tables, runs data-quality checks, and builds the order summary mart.

Generate the business metrics and charts separately:

```bash
python src/business_analysis.py
```

## SQL Analysis

The SQL analysis file contains queries for:

1. Month-over-month revenue and growth.
2. Top product categories by customer state.
3. Seven-day rolling average of daily orders.
4. Repeat purchase rate.
5. Delivery delay compared with review scores.

## Data Quality and Reliability

The pipeline includes checks for missing order IDs, duplicate order IDs, invalid review scores, negative item prices, missing customer matches, and delivery dates before purchase dates.

The raw and staging tables are rebuilt from the source files on each run. The quality-check report is written to `quality_check_results.csv`.

## Metric Definitions

- **Delivered GMV:** Sum of item prices for delivered orders, grouped by purchase month.
- **Delivered Orders:** Number of distinct delivered orders.
- **Repeat Purchase Rate:** Unique customers with more than one order divided by all unique customers.
- **Average Review Score:** Mean available review score for delivered orders.
- **Late Delivery Rate:** Delivered orders with positive delivery delay divided by delivered orders with known delivery delay.

## Security

Database credentials are stored in `.env`. Do not commit `.env`, database passwords, or private credentials to version control.

## Limitations

The pipeline uses full refreshes rather than incremental loading. Results depend on the completeness and quality of the provided source dataset. Business conclusions should be based on the actual SQL outputs and generated charts.
