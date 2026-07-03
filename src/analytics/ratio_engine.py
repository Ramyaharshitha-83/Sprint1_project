import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover
)

DB_PATH = "data/nifty100.db"


def generate_financial_ratios():

    conn = sqlite3.connect(DB_PATH)

    pnl = pd.read_sql("SELECT * FROM profitandloss", conn)
    bs = pd.read_sql("SELECT * FROM balancesheet", conn)

    # Merge P&L and Balance Sheet
    df = pd.merge(
        pnl,
        bs,
        on=["company_id", "year"],
        how="inner"
    )

    results = []

    for _, row in df.iterrows():

        npm = net_profit_margin(
            row["net_profit"],
            row["sales"]
        )

        roe = return_on_equity(
            row["net_profit"],
            row["equity_capital"],
            row["reserves"]
        )

        de_ratio, _ = debt_to_equity(
            row["borrowings"],
            row["equity_capital"],
            row["reserves"]
        )

        icr, label, _ = interest_coverage_ratio(
            row["operating_profit"],
            row["other_income"],
            row["interest"]
        )

        at = asset_turnover(
            row["sales"],
            row["total_assets"]
        )

        results.append({
            "company_id": row["company_id"],
            "year": row["year"],
            "net_profit_margin_pct": npm,
            "return_on_equity_pct": roe,
            "debt_to_equity": de_ratio,
            "interest_coverage": icr,
            "icr_label": label,
            "asset_turnover": at,
            "earnings_per_share": row["eps"],
            "dividend_payout_ratio_pct":
                row["dividend_payout"],
            "total_debt_cr":
                row["borrowings"]
        })

    ratio_df = pd.DataFrame(results)

    ratio_df.to_sql(
        "financial_ratios",
        conn,
        if_exists="replace",
        index=False
    )

    print(
        f"Loaded {len(ratio_df)} ratio rows"
    )

    conn.close()


if __name__ == "__main__":
    generate_financial_ratios()