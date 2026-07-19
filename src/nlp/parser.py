import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output"

# Regex Pattern
REGEX_PATTERN = r"(TTM|Last Year|\d+\s*Years?|\d+\s*Year)\s*:?\s*(-?[\d.]+)\s*%"


def load_data():
    """
    Load analysis and financial ratio tables.
    """

    conn = sqlite3.connect(DB_PATH)

    analysis = pd.read_sql(
        """
        SELECT *
        FROM analysis
        """,
        conn
    )

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr
        FROM financial_ratios
        """,
        conn
    )

    conn.close()

    return analysis, ratios


def parse_text(text):

    if pd.isna(text):
        return None

    text = str(text).strip()

    match = re.search(REGEX_PATTERN, text, re.IGNORECASE)

    if not match:
        return None

    period_text = match.group(1).strip()
    value = float(match.group(2))

    if period_text.upper() == "TTM":
        period = "TTM"
    elif period_text.lower() == "last year":
        period = 1
    else:
        period = int(re.search(r"\d+", period_text).group())

    return period, value


def clean_ratio_value(value):
    """
    Convert CAGR text values into numeric.

    Handles values like:
        15%
        21.4 %
        18

    Returns float or NaN.
    """

    if pd.isna(value):
        return np.nan

    value = str(value)

    value = (
        value
        .replace("%", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(value)

    except Exception:
        return np.nan


def parse_analysis():
    analysis, ratios = load_data()

    parsed_rows = []
    failed_rows = []

    metric_columns = {
        "compounded_sales_growth": "sales_growth",
        "compounded_profit_growth": "profit_growth",
        "stock_price_cagr": "stock_price_cagr",
        "roe": "roe"
    }

    for _, row in analysis.iterrows():

        company = row["company_id"]

        for column, metric_name in metric_columns.items():

            text = row[column]

            result = parse_text(text)

            if result is None:

                failed_rows.append({
                    "company_id": company,
                    "metric_type": metric_name,
                    "original_text": text,
                    "reason": "Regex did not match"
                })

            else:

                period, value = result

                parsed_rows.append({
                    "company_id": company,
                    "metric_type": metric_name,
                    "period_years": period,
                    "value_pct": value
                })

    parsed_df = pd.DataFrame(parsed_rows)

    failures_df = pd.DataFrame(failed_rows)

    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    parsed_path = Path(OUTPUT_DIR) / "analysis_parsed.csv"

    failure_path = Path(OUTPUT_DIR) / "parse_failures.csv"

    parsed_df.to_csv(
        parsed_path,
        index=False
    )

    failures_df.to_csv(
        failure_path,
        index=False
    )

    return (
        parsed_df,
        failures_df,
        ratios,
        parsed_path,
        failure_path
    )


def cross_validate(parsed_df, ratios):

    ratio_mapping = {
        "sales_growth": "revenue_cagr_5yr",
        "profit_growth": "pat_cagr_5yr"
    }

    review_rows = []

    latest_ratios = (
        ratios[ratios["year"] == "Mar 2024"]
        .copy()
    )

    for _, row in parsed_df.iterrows():

        metric = row["metric_type"]

        if metric not in ratio_mapping:
            continue

        ratio_column = ratio_mapping[metric]

        company_data = latest_ratios[
            latest_ratios["company_id"] == row["company_id"]
        ]

        if company_data.empty:
            continue

        ratio_value = clean_ratio_value(
            company_data.iloc[0][ratio_column]
        )

        if pd.isna(ratio_value):
            continue

        parsed_value = row["value_pct"]

        difference = abs(parsed_value - ratio_value)

        if difference > 5:

            review_rows.append({
                "company_id": row["company_id"],
                "metric_type": metric,
                "parsed_value_pct": parsed_value,
                "ratio_engine_value_pct": ratio_value,
                "difference_pct": round(difference, 2)
            })

    review_df = pd.DataFrame(review_rows)

    review_path = (
        Path(OUTPUT_DIR)
        / "cagr_manual_review.csv"
    )

    review_df.to_csv(
        review_path,
        index=False
    )

    return review_df, review_path


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():

    parsed_df, failures_df, ratios, parsed_path, failure_path = parse_analysis()

    review_df, review_path = cross_validate(
        parsed_df,
        ratios
    )

    print("=" * 60)
    print("NLP ANALYSIS PARSER")
    print("=" * 60)

    print(f"Total Parsed Records      : {len(parsed_df)}")
    print(f"Parse Failures           : {len(failures_df)}")
    print(f"Manual Review Required   : {len(review_df)}")

    print()

    print("Generated Files")
    print(f"✓ {parsed_path}")
    print(f"✓ {failure_path}")
    print(f"✓ {review_path}")

    print("=" * 60)


if __name__ == "__main__":
    main()