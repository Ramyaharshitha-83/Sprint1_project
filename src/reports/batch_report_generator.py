import sqlite3
from pathlib import Path

import pandas as pd

from pdf_tearsheet import (
    build_pdf,
    populate_pdf
)


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output/reports"


def load_companies():
    """
    Load all companies from the database.
    """

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        ORDER BY company_name
        """,
        conn
    )

    conn.close()

    return companies


def generate_reports(companies):

    Path(OUTPUT_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    results = []

    for _, row in companies.iterrows():

        company_id = row["company_id"]
        company_name = row["company_name"]

        try:

            (
                elements,
                doc,
                pdf_path,
                valuation,
                pros_cons,
                cashflow,
                capital
            ) = build_pdf(company_id)

            populate_pdf(
                elements,
                doc,
                pdf_path,
                valuation,
                pros_cons,
                cashflow,
                capital
            )

            results.append({
                "company_id": company_id,
                "company_name": company_name,
                "status": "Success",
                "output_file": str(pdf_path)
            })

            print(f"✓ Generated: {company_id}")

        except Exception as e:

            results.append({
                "company_id": company_id,
                "company_name": company_name,
                "status": "Failed",
                "output_file": "",
                "error": str(e)
            })

            print(f"✗ Failed: {company_id} -> {e}")

    return pd.DataFrame(results)


def save_summary(results_df):

    Path(OUTPUT_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    summary_file = (
        Path(OUTPUT_DIR)
        / "batch_report_summary.csv"
    )

    results_df.to_csv(
        summary_file,
        index=False
    )

    summary = {

        "total_companies": len(results_df),

        "success": (
            results_df["status"] == "Success"
        ).sum(),

        "failed": (
            results_df["status"] == "Failed"
        ).sum()

    }

    return summary_file, summary
    # --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    companies = load_companies()

    results_df = generate_reports(companies)

    summary_file, summary = save_summary(results_df)

    print("=" * 60)
    print("BATCH PDF REPORT GENERATION")
    print("=" * 60)

    print(f"Total Companies    : {summary['total_companies']}")
    print(f"Successful Reports : {summary['success']}")
    print(f"Failed Reports     : {summary['failed']}")

    print()
    print("Generated Files")
    print(f"✓ {summary_file}")
    print(f"✓ PDF Reports saved in: {OUTPUT_DIR}")

    print("=" * 60)


if __name__ == "__main__":
    main()