import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output"


def load_data():
    """
    Load capital allocation related metrics.
    """

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            free_cash_flow_cr,
            capex_cr,
            dividend_payout_ratio_pct,
            return_on_equity_pct,
            earnings_per_share,
            book_value_per_share
        FROM financial_ratios
        WHERE year='Mar 2024'
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

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn
    )

    conn.close()

    df = (
        ratios
        .merge(companies, on="company_id", how="left")
        .merge(sectors, on="company_id", how="left")
    )

    df["company_name"] = df["company_name"].str.strip()

    numeric_columns = [
        "free_cash_flow_cr",
        "capex_cr",
        "dividend_payout_ratio_pct",
        "return_on_equity_pct",
        "earnings_per_share",
        "book_value_per_share"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype(str)
                .str.replace("%", "", regex=False)
                .str.replace(",", "", regex=False)
                .replace("", np.nan)
            )

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def analyze_capital_allocation(df):

    records = []

    for _, row in df.iterrows():

        fcf = row["free_cash_flow_cr"]
        capex = row["capex_cr"]
        dividend = row["dividend_payout_ratio_pct"]
        roe = row["return_on_equity_pct"]
        eps = row["earnings_per_share"]
        bvps = row["book_value_per_share"]

        allocation_rating = "Average"
        remarks = []

        # -------------------------
        # Capital Allocation Rating
        # -------------------------

        if (
            pd.notna(fcf)
            and pd.notna(roe)
            and fcf > 0
            and roe >= 20
        ):
            allocation_rating = "Excellent"

        elif (
            pd.notna(fcf)
            and fcf < 0
        ):
            allocation_rating = "Poor"

        elif (
            pd.notna(roe)
            and roe < 10
        ):
            allocation_rating = "Weak"

        # -------------------------
        # Remarks
        # -------------------------

        if pd.notna(dividend):

            if dividend >= 40:
                remarks.append("Strong dividend distribution")

            elif dividend == 0:
                remarks.append("No dividend payout")

        if pd.notna(capex):

            if capex > 0:
                remarks.append("Investing in business expansion")

            else:
                remarks.append("Low capital expenditure")

        if pd.notna(fcf):

            if fcf > 0:
                remarks.append("Positive free cash flow")

            else:
                remarks.append("Negative free cash flow")

        if pd.notna(roe) and roe >= 20:
            remarks.append("Efficient capital utilization")

        if pd.notna(eps) and eps > 0:
            remarks.append("Positive earnings per share")

        if pd.notna(bvps) and bvps > 0:
            remarks.append("Positive book value")

        if len(remarks) == 0:
            remarks.append("No significant observations")

        records.append({

            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "sector": row["broad_sector"],

            "free_cash_flow_cr": fcf,
            "capex_cr": capex,
            "dividend_payout_ratio_pct": dividend,
            "return_on_equity_pct": roe,
            "earnings_per_share": eps,
            "book_value_per_share": bvps,

            "allocation_rating": allocation_rating,
            "remarks": "; ".join(remarks)
        })

    return pd.DataFrame(records)


def save_results(result_df):

    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    output_file = (
        Path(OUTPUT_DIR)
        / "capital_allocation_report.csv"
    )

    result_df.to_csv(
        output_file,
        index=False
    )

    summary = {

        "total_companies": len(result_df),

        "excellent": (
            result_df["allocation_rating"] == "Excellent"
        ).sum(),

        "average": (
            result_df["allocation_rating"] == "Average"
        ).sum(),

        "weak": (
            result_df["allocation_rating"] == "Weak"
        ).sum(),

        "poor": (
            result_df["allocation_rating"] == "Poor"
        ).sum(),

        "average_roe": round(
            result_df["return_on_equity_pct"].mean(skipna=True),
            2
        ),

        "average_dividend": round(
            result_df["dividend_payout_ratio_pct"].mean(skipna=True),
            2
        )
    }

    return output_file, summary
    # --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    df = load_data()

    result_df = analyze_capital_allocation(df)

    output_file, summary = save_results(result_df)

    print("=" * 60)
    print("CAPITAL ALLOCATION REPORT")
    print("=" * 60)

    print(f"Companies Processed     : {summary['total_companies']}")
    print(f"Excellent Rating        : {summary['excellent']}")
    print(f"Average Rating          : {summary['average']}")
    print(f"Weak Rating             : {summary['weak']}")
    print(f"Poor Rating             : {summary['poor']}")
    print(f"Average ROE             : {summary['average_roe']}")
    print(f"Average Dividend Payout : {summary['average_dividend']}")

    print()

    print("Generated Files")
    print(f"✓ {output_file}")

    print("=" * 60)


if __name__ == "__main__":
    main()