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
    TableStyle
)


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output/reports"


def load_company_data(company_id):
    """
    Load all required data for a company.
    """

    conn = sqlite3.connect(DB_PATH)

    company = pd.read_sql(
        f"""
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector
        FROM companies c
        LEFT JOIN sectors s
        ON c.id = s.company_id
        WHERE c.id = '{company_id}'
        """,
        conn
    )

    ratios = pd.read_sql(
        f"""
        SELECT *
        FROM financial_ratios
        WHERE company_id='{company_id}'
        AND year='Mar 2024'
        """,
        conn
    )

    valuation = pd.read_excel(
        "output/valuation_summary.xlsx"
    )

    pros_cons = pd.read_csv(
        "output/pros_cons_generated.csv"
    )

    cashflow = pd.read_csv(
        "output/cashflow_intelligence.csv"
    )

    capital = pd.read_csv(
        "output/capital_allocation_report.csv"
    )

    conn.close()

    valuation = valuation[
        valuation["company_id"] == company_id
    ]

    pros_cons = pros_cons[
        pros_cons["company_id"] == company_id
    ]

    cashflow = cashflow[
        cashflow["company_id"] == company_id
    ]

    capital = capital[
        capital["company_id"] == company_id
    ]

    return (
        company,
        ratios,
        valuation,
        pros_cons,
        cashflow,
        capital
    )


def build_pdf(company_id):

    (
        company,
        ratios,
        valuation,
        pros_cons,
        cashflow,
        capital
    ) = load_company_data(company_id)

    if ratios.empty:
        raise ValueError(f"No financial ratio data found for {company_id}")

    Path(OUTPUT_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    pdf_path = (
        Path(OUTPUT_DIR)
        / f"{company_id}_tearsheet.pdf"
    )

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=(8.27 * inch, 11.69 * inch)
    )

    elements = []

    # --------------------------------------------------
    # Title
    # --------------------------------------------------

    company_name = company.iloc[0]["company_name"]

    sector = company.iloc[0]["broad_sector"]

    elements.append(
        Paragraph(
            f"<b>{company_name}</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"Sector : {sector}",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 0.25 * inch)
    )

    # --------------------------------------------------
    # Financial Ratios
    # --------------------------------------------------

    ratio = ratios.iloc[0]

    ratio_table = [

        ["Metric", "Value"],

        [
            "ROE (%)",
            ratio["return_on_equity_pct"]
        ],

        [
            "Net Profit Margin (%)",
            ratio["net_profit_margin_pct"]
        ],

        [
            "Debt / Equity",
            ratio["debt_to_equity"]
        ],

        [
            "P/E",
            ratio["pe_ratio"]
        ],

        [
            "P/B",
            ratio["pb_ratio"]
        ],

        [
            "Dividend Yield (%)",
            ratio["dividend_yield_pct"]
        ]
    ]

    table = Table(
        ratio_table,
        colWidths=[3 * inch, 2 * inch]
    )

    table.setStyle(

        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

            ("ALIGN", (1, 1), (-1, -1), "CENTER")

        ])
    )

    elements.append(table)

    elements.append(
        Spacer(1, 0.25 * inch)
    )

    return (
        elements,
        doc,
        pdf_path,
        valuation,
        pros_cons,
        cashflow,
        capital
    )


def populate_pdf(
    elements,
    doc,
    pdf_path,
    valuation,
    pros_cons,
    cashflow,
    capital
):

    styles = getSampleStyleSheet()

    # --------------------------------------------------
    # Valuation
    # --------------------------------------------------

    elements.append(
        Paragraph("<b>Valuation Summary</b>", styles["Heading2"])
    )

    if not valuation.empty:

        val = valuation.iloc[0]

        valuation_table = [
            ["Metric", "Value"],
            ["P/E", val.get("pe_ratio", "N/A")],
            ["P/B", val.get("pb_ratio", "N/A")],
            ["Dividend Yield", val.get("dividend_yield_pct", "N/A")],
            ["FCF Yield", val.get("fcf_yield_pct", "N/A")],
            ["Valuation Flag", val.get("valuation_flag", "N/A")]
        ]

        table = Table(
            valuation_table,
            colWidths=[3 * inch, 2 * inch]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)
        ]))

        elements.append(table)

    elements.append(Spacer(1, 0.20 * inch))

    # --------------------------------------------------
    # Pros & Cons
    # --------------------------------------------------

    elements.append(
        Paragraph("<b>Pros & Cons</b>", styles["Heading2"])
    )

    if not pros_cons.empty:

        pc = pros_cons.iloc[0]

        elements.append(
            Paragraph(
                f"<b>Pros:</b> {pc['pros']}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Cons:</b> {pc['cons']}",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 0.20 * inch))

    # --------------------------------------------------
    # Cash Flow
    # --------------------------------------------------

    elements.append(
        Paragraph("<b>Cash Flow Intelligence</b>", styles["Heading2"])
    )

    if not cashflow.empty:

        cf = cashflow.iloc[0]

        elements.append(
            Paragraph(
                f"Health: {cf['cashflow_health']}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Warnings: {cf['warnings']}",
                styles["BodyText"]
            )
        )

    elements.append(Spacer(1, 0.20 * inch))

    # --------------------------------------------------
    # Capital Allocation
    # --------------------------------------------------

    elements.append(
        Paragraph("<b>Capital Allocation</b>", styles["Heading2"])
    )

    if not capital.empty:

        cap = capital.iloc[0]

        elements.append(
            Paragraph(
                f"Rating: {cap['allocation_rating']}",
                styles["BodyText"]
            )
        )

        elements.append(
            Paragraph(
                f"Remarks: {cap['remarks']}",
                styles["BodyText"]
            )
        )

    doc.build(elements)

    return pdf_path
    # --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    # Change this company ID to generate a report
    company_id = "ABB"

    (
        elements,
        doc,
        pdf_path,
        valuation,
        pros_cons,
        cashflow,
        capital
    ) = build_pdf(company_id)

    pdf_path = populate_pdf(
        elements,
        doc,
        pdf_path,
        valuation,
        pros_cons,
        cashflow,
        capital
    )

    print("=" * 60)
    print("PDF TEARSHEET GENERATED")
    print("=" * 60)
    print(f"Company : {company_id}")
    print(f"Output  : {pdf_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()