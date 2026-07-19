import sqlite3
from pathlib import Path

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

DB_PATH = "data/nifty100.db"
REPORT_DIR = "output/reports"


def load_data():
    """
    Load data required for portfolio summary.
    """

    conn = sqlite3.connect(DB_PATH)

    financial = pd.read_sql(
        """
        SELECT
            company_id,
            return_on_equity_pct,
            composite_quality_score
        FROM financial_ratios
        WHERE year='Mar 2024'
        """,
        conn,
    )

    conn.close()

    batch = pd.read_csv(
        Path(REPORT_DIR) / "batch_report_summary.csv"
    )

    cashflow = pd.read_csv(
        "output/cashflow_intelligence.csv"
    )

    capital = pd.read_csv(
        "output/capital_allocation_report.csv"
    )

    return financial, batch, cashflow, capital


def calculate_statistics(financial, batch, cashflow, capital):
    """
    Calculate portfolio-level summary statistics.
    """

    summary = {}

    # Batch report statistics
    summary["total_companies"] = len(batch)
    summary["successful_reports"] = (batch["status"] == "Success").sum()
    summary["failed_reports"] = (batch["status"] == "Failed").sum()

    # Cash Flow Health
    summary["healthy_cashflow"] = (
        cashflow["cashflow_health"] == "Healthy"
    ).sum()

    summary["warning_cashflow"] = (
        cashflow["cashflow_health"] == "Warning"
    ).sum()

    summary["critical_cashflow"] = (
        cashflow["cashflow_health"] == "Critical"
    ).sum()

    # Capital Allocation Ratings
    summary["excellent_allocation"] = (
        capital["allocation_rating"] == "Excellent"
    ).sum()

    summary["average_allocation"] = (
        capital["allocation_rating"] == "Average"
    ).sum()

    summary["weak_allocation"] = (
        capital["allocation_rating"] == "Weak"
    ).sum()

    summary["poor_allocation"] = (
        capital["allocation_rating"] == "Poor"
    ).sum()

    # Average metrics
    summary["average_roe"] = round(
        financial["return_on_equity_pct"].mean(), 2
    )

    if financial["composite_quality_score"].dropna().empty:
        summary["average_quality_score"] = "N/A"
    else:
        summary["average_quality_score"] = round(
            financial["composite_quality_score"].mean(), 2
        )

    # Top 10 companies by Quality Score
    top_companies = (
        financial.sort_values(
            "return_on_equity_pct",
            ascending=False
        )
        .head(10)
        .reset_index(drop=True)
    )

    return summary, top_companies


def build_pdf(summary, top_companies):
    """
    Build the portfolio summary PDF.
    """

    Path(REPORT_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    pdf_path = (
        Path(REPORT_DIR)
        / "portfolio_summary.pdf"
    )

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=(8.5 * inch, 11 * inch)
    )

    styles = getSampleStyleSheet()

    elements = []

    # --------------------------------------------------
    # Title
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Portfolio Summary Report</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "Sprint 5 Final Deliverable",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 0.3 * inch))

    # --------------------------------------------------
    # Portfolio Summary
    # --------------------------------------------------

    summary_table = [
        ["Metric", "Value"],
        ["Total Companies", summary["total_companies"]],
        ["Successful Reports", summary["successful_reports"]],
        ["Failed Reports", summary["failed_reports"]],
        ["Average ROE (%)", summary["average_roe"]],
        ["Average Quality Score", summary["average_quality_score"]],
    ]

    table = Table(summary_table, colWidths=[3.5 * inch, 2 * inch])

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    )

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    # --------------------------------------------------
    # Cash Flow Health
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Cash Flow Health</b>",
            styles["Heading2"]
        )
    )

    cashflow_table = [
        ["Healthy", summary["healthy_cashflow"]],
        ["Warning", summary["warning_cashflow"]],
        ["Critical", summary["critical_cashflow"]],
    ]

    cf_table = Table(cashflow_table)

    cf_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )

    elements.append(cf_table)
    elements.append(Spacer(1, 0.3 * inch))

    # --------------------------------------------------
    # Capital Allocation
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Capital Allocation</b>",
            styles["Heading2"]
        )
    )

    capital_table = [
        ["Excellent", summary["excellent_allocation"]],
        ["Average", summary["average_allocation"]],
        ["Weak", summary["weak_allocation"]],
        ["Poor", summary["poor_allocation"]],
    ]

    cap_table = Table(capital_table)

    cap_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )

    elements.append(cap_table)
    elements.append(Spacer(1, 0.3 * inch))

    # --------------------------------------------------
    # Top Companies
    # --------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Top 10 Companies by Quality Score</b>",
            styles["Heading2"]
        )
    )

    top_table = [["Company ID", "ROE (%)"]]

    for _, row in top_companies.iterrows():
        top_table.append([
            row["company_id"],
            row["return_on_equity_pct"]
        ])

    top = Table(top_table)

    top.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    )

    elements.append(top)

    doc.build(elements)

    return pdf_path
    # --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    financial, batch, cashflow, capital = load_data()

    summary, top_companies = calculate_statistics(
        financial,
        batch,
        cashflow,
        capital
    )

    pdf_path = build_pdf(
        summary,
        top_companies
    )

    print("=" * 60)
    print("PORTFOLIO SUMMARY REPORT")
    print("=" * 60)
    print(f"Total Companies      : {summary['total_companies']}")
    print(f"Successful Reports   : {summary['successful_reports']}")
    print(f"Failed Reports       : {summary['failed_reports']}")
    print(f"Average ROE          : {summary['average_roe']} %")
    print(f"Average Quality Score: {summary['average_quality_score']}")
    print()
    print("Generated Files")
    print(f"✓ {pdf_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()