import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "data/nifty100.db"

LOG_FILE = "output/ratio_edge_cases.log"

Path("output").mkdir(exist_ok=True)


def review_edge_cases():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    merged = pd.merge(
        ratios,
        companies,
        left_on="company_id",
        right_on="id",
        how="left"
    )

    log_lines = []

    # ROE anomalies

    for _, row in merged.iterrows():

        source_roe = row.get(
            "roe_percentage"
        )

        computed_roe = row.get(
            "return_on_equity_pct"
        )

        if pd.notna(source_roe) and \
           pd.notna(computed_roe):

            diff = abs(
                source_roe - computed_roe
            )

            if diff > 5:

                log_lines.append(
                    f"[ROE] "
                    f"{row['company_id']} | "
                    f"Source={source_roe} | "
                    f"Computed={computed_roe} | "
                    f"Category=Formula Difference"
                )

    # Financial sector carve-out

    financial_companies = merged[
        merged["company_name"]
        .str.contains(
            "BANK|FINANCE|INSURANCE",
            case=False,
            na=False
        )
    ]

    for _, row in financial_companies.iterrows():

        log_lines.append(
            f"[LEVERAGE SUPPRESSED] "
            f"{row['company_id']} | "
            f"Financial sector company"
        )

    with open(LOG_FILE, "w") as f:

        for line in log_lines:
            f.write(line + "\n")

    print(
        f"{len(log_lines)} "
        f"edge cases logged."
    )

    conn.close()


if __name__ == "__main__":
    review_edge_cases()