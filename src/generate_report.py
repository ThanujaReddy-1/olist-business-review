from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether
)

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
OUTPUT = REPORTS / "weekly_business_review_v1.pdf"
METRICS_CSV = REPORTS / "business_metrics.csv"

# Read project-generated metrics when available; otherwise use the values
# shared during the project conversation.
metrics = {
    "Monthly Delivered GMV": "838576.64",
    "Repeat Purchase Rate": "3.12%",
    "Average Review Score": "4.16",
    "Late Delivery Rate": "8.11%",
}
if METRICS_CSV.exists():
    try:
        df = pd.read_csv(METRICS_CSV)
        if {"metric", "value"}.issubset(df.columns):
            metrics.update(dict(zip(df["metric"].astype(str), df["value"].astype(str))))
    except Exception as exc:
        print(f"Could not read metrics CSV; using conversation-provided values: {exc}")

def metric(name):
    return metrics.get(name, "Not available")

doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4,
    rightMargin=1.35 * cm, leftMargin=1.35 * cm,
    topMargin=1.25 * cm, bottomMargin=1.25 * cm
)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="MainTitle", parent=styles["Title"], alignment=TA_CENTER,
    textColor=colors.HexColor("#163A5F"), fontSize=21, leading=25,
    spaceAfter=4
))
styles.add(ParagraphStyle(
    name="Subtitle", parent=styles["Normal"], alignment=TA_CENTER,
    textColor=colors.HexColor("#526579"), fontSize=8.5, leading=11,
    spaceAfter=10
))
styles.add(ParagraphStyle(
    name="SectionHeading", parent=styles["Heading2"],
    textColor=colors.HexColor("#176B87"), fontSize=11.5, leading=13,
    spaceBefore=4, spaceAfter=4
))
styles.add(ParagraphStyle(
    name="BodyCompact", parent=styles["BodyText"],
    fontSize=8, leading=10, spaceAfter=4
))
styles.add(ParagraphStyle(
    name="Caption", parent=styles["BodyText"],
    fontSize=7, leading=8.5, textColor=colors.HexColor("#526579"),
    spaceAfter=3
))
styles.add(ParagraphStyle(
    name="Memo", parent=styles["BodyText"],
    fontSize=8.2, leading=10.5, spaceAfter=5
))

story = []

def para(text, style="BodyCompact"):
    story.append(Paragraph(text, styles[style]))

def section(text):
    story.append(Paragraph(text, styles["SectionHeading"]))

def add_chart(filename, caption, max_w=16.8 * cm, max_h=6.1 * cm):
    path = REPORTS / filename
    if not path.exists():
        para(f"<b>Chart not found:</b> {filename}", "Caption")
        return
    img = Image(str(path))
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
    img.drawWidth = img.imageWidth * scale
    img.drawHeight = img.imageHeight * scale
    story.append(img)
    para(caption, "Caption")

def make_table(data, widths, font_size=7.2):
    tbl = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#163A5F")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#CBD5DF")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F2F6FA")]),
        ("FONTSIZE", (0,0), (-1,-1), font_size),
        ("LEADING", (0,0), (-1,-1), font_size + 1.5),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return tbl

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E2EA"))
    canvas.line(1.35*cm, 0.95*cm, A4[0]-1.35*cm, 0.95*cm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#526579"))
    canvas.drawString(1.35*cm, 0.65*cm, "Olist Marketplace | Business Data Analysis")
    canvas.drawRightString(A4[0]-1.35*cm, 0.65*cm, f"{doc.page} / 5")
    canvas.restoreState()

# PAGE 1 — What I built and business metrics
story.append(Paragraph("E-commerce Data Analysis", styles["MainTitle"]))
story.append(Paragraph(
    "BDA Take-Home Assignment | Olist Brazilian E-commerce Dataset",
    styles["Subtitle"]
))
section("1. What I Built")
para(
    "I built a Python-based ELT pipeline to load the Olist CSV files into PostgreSQL, "
    "prepare cleaned staging tables, run SQL data-quality checks, and create an "
    "analysis-ready order-level mart. A separate analysis script calculates business "
    "metrics and saves four PNG charts. Five SQL analyses answer the assignment's "
    "business questions using aggregations, CTEs, and window functions."
)
flow_data = [
    ["Pipeline stage", "Purpose", "Output"],
    ["Raw ingestion", "Load source CSV files and validate expected inputs", "raw_* tables"],
    ["Staging", "Standardise and prepare order, item, payment, review, customer and product data", "stg_* tables"],
    ["Data quality", "Check missing IDs, duplicates, invalid scores, negative prices, customer links and dates", "Logged results / CSV"],
    ["Order mart", "Combine order-level revenue, freight, payment, review and delivery information", "mart_order_summary"],
    ["Business analysis", "Calculate KPIs and produce charts", "business_metrics.csv + 4 PNGs"],
]
story.append(make_table(flow_data, [2.6*cm, 8.2*cm, 5.8*cm], 7))
story.append(Spacer(1, 5))
section("North Star and Supporting Metrics")
kpi_data = [
    ["Metric", "Result", "Formula / purpose"],
    ["Monthly Delivered GMV", metric("Monthly Delivered GMV"), "Sum of item prices for delivered orders; excludes freight and is not profit."],
    ["Repeat Purchase Rate", metric("Repeat Purchase Rate"), "Unique customers with >1 order / all unique customers."],
    ["Average Review Score", metric("Average Review Score") + " / 5", "Average review score for delivered orders."],
    ["Late Delivery Rate", metric("Late Delivery Rate"), "Late delivered orders / delivered orders with known delay."],
]
story.append(make_table(kpi_data, [3.6*cm, 2.3*cm, 10.7*cm], 7))
para(
    "The metrics provide a baseline for tracking revenue, retention, customer feedback and delivery reliability. "
    "The GMV reporting period and currency should be labelled from the underlying monthly output.",
    "Caption"
)
story.append(PageBreak())

# PAGE 2 — Data quality
section("2. Data-Quality Checks")
para(
    "The pipeline runs quality checks before relying on the order mart. The reported pipeline validation "
    "showed the checks passing. These checks protect against common structural and business-rule issues."
)
quality_data = [
    ["Check", "What it catches", "Why it matters"],
    ["Missing order IDs", "Null order identifiers", "Prevents untraceable order records"],
    ["Duplicate order IDs", "Repeated order identifiers in the mart", "Supports one row per order"],
    ["Invalid review scores", "Scores outside the allowed 1–5 range", "Protects satisfaction metrics"],
    ["Negative item prices", "Prices below zero", "Prevents invalid revenue calculations"],
    ["Missing customers", "Orders without a matching customer", "Protects customer-level analysis"],
    ["Delivery before purchase", "Delivery timestamp earlier than purchase", "Flags invalid event chronology"],
]
story.append(make_table(quality_data, [3.4*cm, 6.0*cm, 7.2*cm], 7.2))
story.append(Spacer(1, 6))
section("Handling and reliability")
para(
    "The checks log their outcomes and raise an error when a configured check fails. This fail-fast behaviour "
    "prevents the pipeline from silently continuing with data that violates its validation rules. The quality "
    "results CSV should be retained with the run outputs for auditability."
)
section("Order-mart validation")
para(
    "The order mart was checked for one row per order: total rows matched distinct order IDs (99,441), "
    "and the duplicate-order query returned no rows. The quality checks were reported as passed in the run "
    "described during project development."
)
section("Why these checks matter")
para(
    "Data quality affects downstream conclusions. Duplicate orders can inflate revenue and order counts; "
    "invalid prices can distort GMV; missing customers can understate customer analysis; and incorrect dates "
    "can misclassify delivery performance."
)
story.append(PageBreak())

# PAGE 3 — SQL analysis and charts 1–2
section("3. SQL Analysis")
para(
    "Five SQL-only analyses use CTEs, grouping, date handling and window functions. They are saved in "
    "sql/analysis_queries.sql and run against the staging tables and order mart."
)
sql_data = [
    ["Business question", "SQL approach", "Business use"],
    ["Monthly revenue and growth", "Monthly aggregation + LAG()", "Tracks month-over-month revenue change."],
    ["Top 3 categories per state", "Category/state revenue + DENSE_RANK()", "Shows leading categories by customer geography."],
    ["Seven-day rolling orders", "Daily counts + window frame", "Smooths daily volatility and reveals order trends."],
    ["Repeat purchase rate", "COUNT(DISTINCT order_id) by customer_unique_id", "Measures how many customers return."],
    ["Delivery delay vs reviews", "Delay categories + average review score", "Explores association between delivery and satisfaction."],
]
story.append(make_table(sql_data, [4.0*cm, 6.0*cm, 6.6*cm], 7.1))
story.append(Spacer(1, 6))
para(
    "Interpretation note: a seven-row rolling window is a seven-calendar-day average only when the date series "
    "contains every calendar date. Missing dates should be filled with zero before calculating the rolling window."
)
add_chart("monthly_gmv.png",
          "Figure 1. Monthly delivered GMV — use this trend to spot revenue peaks, declines and possible seasonality.",
          max_h=6.0*cm)
add_chart("monthly_orders.png",
          "Figure 2. Delivered-order volume — compare with GMV to separate order-volume changes from value-per-order changes.",
          max_h=5.6*cm)
story.append(PageBreak())

# PAGE 4 — Remaining charts and findings
section("4. Business Charts and Findings")
para(
    f"The reported average review score is {metric('Average Review Score')} / 5 and the reported late delivery "
    f"rate is {metric('Late Delivery Rate')}. Review the delivery chart for differences between timing groups; "
    "an observed relationship does not establish causation."
)
add_chart("delivery_vs_review.png",
          "Figure 3. Delivery timing versus reviews — compare review scores across delivery categories.")
add_chart("order_status.png",
          "Figure 4. Order status distribution — provides context on delivered orders and other order outcomes.")
section("What to monitor next")
findings_data = [
    ["Area", "Signal to monitor", "Follow-up question"],
    ["Revenue", "Monthly delivered GMV", "Does revenue move with delivered-order volume?"],
    ["Retention", "Repeat purchase rate", "Which customer groups return, and how does this change over time?"],
    ["Customer experience", "Average review score", "Are lower scores concentrated in certain delivery groups or categories?"],
    ["Operations", "Late delivery rate", "Which states, sellers or categories have the highest late-delivery rates?"],
]
story.append(make_table(findings_data, [3.0*cm, 4.6*cm, 9.0*cm], 7.1))
story.append(PageBreak())

# PAGE 5 — VP memo and conclusion
section("5. Memo to the Vice President")
memo_data = [
    ["To", "Vice President, Marketplace Operations"],
    ["Subject", "Marketplace performance and data reliability"],
    ["Purpose", "Summarise the current baseline and recommend next actions"],
]
story.append(make_table(memo_data, [2.4*cm, 14.2*cm], 7.5))
story.append(Spacer(1, 7))
para(
    "<b>Executive message.</b> The pipeline now provides a repeatable view of delivered-item revenue, "
    "customer retention, review scores and delivery reliability. Current reported measures are "
    f"GMV {metric('Monthly Delivered GMV')}, repeat purchase rate {metric('Repeat Purchase Rate')}, "
    f"average review score {metric('Average Review Score')}/5, and late delivery rate {metric('Late Delivery Rate')}."
    , "Memo"
)
para(
    "<b>Recommended actions.</b> First, investigate late deliveries by state, seller and category. "
    "Second, monitor repeat purchase rate over time and evaluate targeted retention initiatives. "
    "Third, compare review scores across delivery groups to identify customer-experience opportunities. "
    "Finally, review data-quality outputs before each business review so metric changes are not driven by "
    "unnoticed data issues.", "Memo"
)
para(
    "<b>Decision requested.</b> Prioritise a delivery-performance deep dive and establish a recurring KPI "
    "review that tracks GMV, delivered orders, repeat purchasing, review scores and late delivery rate. "
    "Validate trends over multiple periods before attributing results to a specific action.", "Memo"
)
section("Conclusion")
para(
    "The project combines an auditable data pipeline, explicit data-quality checks, five SQL analyses and "
    "four charts into a compact business-review workflow. The metrics establish a baseline; the next step is "
    "to compare periods, investigate the largest segment-level changes and use verified findings to guide "
    "operational decisions."
)
para(
    "Source: Olist Brazilian E-commerce dataset and project-generated pipeline outputs. "
    "This is descriptive analysis; relationships do not by themselves prove causation.",
    "Caption"
)

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"PDF report created: {OUTPUT}")
print("Please open the PDF and verify page count, metric values, and chart readability.")
