import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output"


def load_data():
    """
    Load financial ratios for cash flow analysis.
    """

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            free_cash_flow_cr,
            cash_from_operations_cr,
            capex_cr
        FROM financial_ratios
        """,
        conn
    )

    companies = pd.read_sql(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        """,
        conn
    )

    conn.close()

    df = ratios.merge(
        companies,
        on="company_id",
        how="left"
    )

    df["company_name"] = df["company_name"].str.strip()

    numeric_columns = [
        "free_cash_flow_cr",
        "cash_from_operations_cr",
        "capex_cr"
    ]

    for column in numeric_columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .replace("", np.nan)
        )

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def analyze_cashflow(df):

    records = []

    latest_df = (
        df[df["year"] == "Mar 2024"]
        .copy()
    )

    for _, row in latest_df.iterrows():

        health = "Healthy"
        warnings = []

        fcf = row["free_cash_flow_cr"]
        cfo = row["cash_from_operations_cr"]
        capex = row["capex_cr"]

        # -------------------------
        # Health Assessment
        # -------------------------

        if pd.isna(cfo):
            health = "Unknown"

        elif cfo < 0:
            health = "Critical"
            warnings.append("Negative Operating Cash Flow")

        elif fcf < 0:
            health = "Warning"
            warnings.append("Negative Free Cash Flow")

        elif cfo > 0 and fcf > 0:
            health = "Healthy"

        # -------------------------
        # Additional Checks
        # -------------------------

        if capex > cfo:
            warnings.append("Capital Expenditure exceeds Operating Cash Flow")

        if cfo > 0 and capex > 0:

            reinvestment_ratio = round(capex / cfo, 2)

        else:

            reinvestment_ratio = np.nan

        if (
            not pd.isna(reinvestment_ratio)
            and reinvestment_ratio > 1
        ):
            warnings.append("Very High Reinvestment Ratio")

        if len(warnings) == 0:
            warnings.append("No major cash flow concerns")

        records.append({

            "company_id": row["company_id"],
            "company_name": row["company_name"],

            "cash_from_operations_cr": cfo,
            "free_cash_flow_cr": fcf,
            "capex_cr": capex,

            "reinvestment_ratio": reinvestment_ratio,

            "cashflow_health": health,

            "warnings": "; ".join(warnings)
        })

    return pd.DataFrame(records)


def save_results(result_df):

    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    output_file = (
        Path(OUTPUT_DIR)
        / "cashflow_intelligence.csv"
    )

    result_df.to_csv(
        output_file,
        index=False
    )

    summary = {

        "total_companies": len(result_df),

        "healthy": (
            result_df["cashflow_health"] == "Healthy"
        ).sum(),

        "warning": (
            result_df["cashflow_health"] == "Warning"
        ).sum(),

        "critical": (
            result_df["cashflow_health"] == "Critical"
        ).sum(),

        "unknown": (
            result_df["cashflow_health"] == "Unknown"
        ).sum(),

        "average_reinvestment_ratio": round(
            result_df["reinvestment_ratio"].mean(skipna=True),
            2
        )
    }

    return output_file, summary
    # --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    df = load_data()

    result_df = analyze_cashflow(df)

    output_file, summary = save_results(result_df)

    print("=" * 60)
    print("CASH FLOW INTELLIGENCE")
    print("=" * 60)

    print(f"Companies Processed        : {summary['total_companies']}")
    print(f"Healthy Companies         : {summary['healthy']}")
    print(f"Warning Companies         : {summary['warning']}")
    print(f"Critical Companies        : {summary['critical']}")
    print(f"Unknown Companies         : {summary['unknown']}")
    print(
        f"Average Reinvestment Ratio: "
        f"{summary['average_reinvestment_ratio']}"
    )

    print()
    print("Generated Files")
    print(f"✓ {output_file}")

    print("=" * 60)


if __name__ == "__main__":
    main()