import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output"


def load_data():
    """
    Load financial ratios and company details.
    """

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT *
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

    numeric_columns = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "dividend_payout_ratio_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
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


def generate_pros_cons(df):

    records = []

    for _, row in df.iterrows():

        pros = []
        cons = []

        # -------------------------
        # PRO RULES
        # -------------------------

        if row["return_on_equity_pct"] >= 20:
            pros.append("High Return on Equity")

        if row["net_profit_margin_pct"] >= 15:
            pros.append("Strong Profit Margin")

        if row["operating_profit_margin_pct"] >= 20:
            pros.append("Healthy Operating Margin")

        if row["debt_to_equity"] <= 0.5:
            pros.append("Low Debt")

        if row["interest_coverage"] >= 5:
            pros.append("Comfortable Interest Coverage")

        if row["asset_turnover"] >= 1:
            pros.append("Efficient Asset Utilization")

        if row["free_cash_flow_cr"] > 0:
            pros.append("Positive Free Cash Flow")

        if row["dividend_payout_ratio_pct"] >= 20:
            pros.append("Consistent Dividend Payout")

        if row["revenue_cagr_5yr"] >= 10:
            pros.append("Healthy Revenue Growth")

        if row["pat_cagr_5yr"] >= 10:
            pros.append("Strong Profit Growth")

        if row["eps_cagr_5yr"] >= 10:
            pros.append("Growing Earnings Per Share")

        if row["composite_quality_score"] >= 75:
            pros.append("High Overall Quality Score")

        # -------------------------
        # CON RULES
        # -------------------------

        if row["return_on_equity_pct"] < 10:
            cons.append("Low Return on Equity")

        if row["net_profit_margin_pct"] < 5:
            cons.append("Weak Profit Margin")

        if row["operating_profit_margin_pct"] < 10:
            cons.append("Weak Operating Margin")

        if row["debt_to_equity"] > 2:
            cons.append("High Debt")

        if row["interest_coverage"] < 2:
            cons.append("Low Interest Coverage")

        if row["asset_turnover"] < 0.5:
            cons.append("Poor Asset Utilization")

        if row["free_cash_flow_cr"] < 0:
            cons.append("Negative Free Cash Flow")

        if row["dividend_payout_ratio_pct"] == 0:
            cons.append("No Dividend")

        if row["revenue_cagr_5yr"] < 5:
            cons.append("Slow Revenue Growth")

        if row["pat_cagr_5yr"] < 5:
            cons.append("Weak Profit Growth")

        if row["eps_cagr_5yr"] < 5:
            cons.append("Weak EPS Growth")

        if row["composite_quality_score"] < 40:
            cons.append("Low Overall Quality Score")

        # Ensure at least one pro/con

        if len(pros) == 0:
            pros.append("Business has stable fundamentals")

        if len(cons) == 0:
            cons.append("No major financial concerns")

        confidence = min(
            100,
            50 + (len(pros) * 5) + (len(cons) * 2)
        )

        records.append({

            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "sector": row["broad_sector"],

            "pros": "; ".join(pros),
            "cons": "; ".join(cons),

            "pros_count": len(pros),
            "cons_count": len(cons),

            "confidence_score": confidence
        })

    return pd.DataFrame(records)


def save_results(result_df):

    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    output_file = (
        Path(OUTPUT_DIR)
        / "pros_cons_generated.csv"
    )

    result_df.to_csv(
        output_file,
        index=False
    )

    summary = {
        "total_companies": len(result_df),
        "average_pros": round(result_df["pros_count"].mean(), 2),
        "average_cons": round(result_df["cons_count"].mean(), 2),
        "average_confidence": round(
            result_df["confidence_score"].mean(),
            2
        ),
        "highest_confidence": result_df["confidence_score"].max(),
        "lowest_confidence": result_df["confidence_score"].min()
    }

    return output_file, summary
    # --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    df = load_data()

    result_df = generate_pros_cons(df)

    output_file, summary = save_results(result_df)

    print("=" * 60)
    print("AUTO PROS & CONS GENERATOR")
    print("=" * 60)

    print(f"Companies Processed     : {summary['total_companies']}")
    print(f"Average Pros            : {summary['average_pros']}")
    print(f"Average Cons            : {summary['average_cons']}")
    print(f"Average Confidence      : {summary['average_confidence']}")
    print(f"Highest Confidence      : {summary['highest_confidence']}")
    print(f"Lowest Confidence       : {summary['lowest_confidence']}")

    print()
    print("Generated Files")
    print(f"✓ {output_file}")

    print("=" * 60)


if __name__ == "__main__":
    main()