import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover
)

from src.analytics.cashflow_kpis import (
    free_cash_flow
)

DB_PATH = "data/nifty100.db"


def normalize_year(value):
    """
    Converts:
    Mar 2014 -> 2014
    Dec 2012 -> 2012
    2014 -> 2014
    TTM -> None
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.upper() == "TTM":
        return None

    if value.isdigit():
        return int(value)

    try:
        return int(value.split()[-1])
    except:
        return None


def load_tables():

    conn = sqlite3.connect(DB_PATH)

    pnl = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn
    )

    bs = pd.read_sql(
        "SELECT * FROM balancesheet",
        conn
    )

    cf = pd.read_sql(
        "SELECT * FROM cashflow",
        conn
    )

    mc = pd.read_sql(
        "SELECT * FROM market_cap",
        conn
    )

    conn.close()

    # Normalize years
    pnl["merge_year"] = pnl["year"].apply(normalize_year)
    bs["merge_year"] = bs["year"].apply(normalize_year)
    cf["merge_year"] = cf["year"].apply(normalize_year)
    mc["merge_year"] = mc["year"]

    # Remove duplicate company-year records
    pnl = pnl.drop_duplicates(
        subset=["company_id", "merge_year"],
        keep="first"
    )

    bs = bs.drop_duplicates(
        subset=["company_id", "merge_year"],
        keep="first"
    )

    cf = cf.drop_duplicates(
        subset=["company_id", "merge_year"],
        keep="first"
    )

    mc = mc.drop_duplicates(
        subset=["company_id", "merge_year"],
        keep="first"
    )

    return pnl, bs, cf, mc


def merge_tables():

    pnl, bs, cf, mc = load_tables()

    # Merge Profit & Loss + Balance Sheet
    df = pnl.merge(
        bs,
        on=["company_id", "merge_year"],
        how="left",
        suffixes=("_pnl", "_bs")
    )

    # Merge Cash Flow
    df = df.merge(
        cf,
        on=["company_id", "merge_year"],
        how="left",
        suffixes=("", "_cf")
    )

    # Merge Market Cap
    df = df.merge(
        mc,
        on=["company_id", "merge_year"],
        how="left",
        suffixes=("", "_mc")
    )

    print("=" * 60)
    print("Merged Rows:", len(df))
    print("=" * 60)

    print(df.head())

    return df

def generate_financial_ratios():

    df = merge_tables()

    results = []

    for _, row in df.iterrows():

        # Profitability Ratios
        npm = net_profit_margin(
            row["net_profit"],
            row["sales"]
        )

        opm = row["opm_percentage"]

        roe = return_on_equity(
            row["net_profit"],
            row["equity_capital"],
            row["reserves"]
        )

        # Leverage Ratios
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

        # Efficiency
        at = asset_turnover(
            row["sales"],
            row["total_assets"]
        )

        # Cash Flow KPIs
        fcf = free_cash_flow(
            row["operating_activity"],
            row["investing_activity"]
        )

        cfo = row["operating_activity"]

        capex = (
            abs(row["investing_activity"])
            if pd.notna(row["investing_activity"])
            else None
        )

        # Book Value Per Share
        if (
            pd.notna(row["equity_capital"])
            and row["equity_capital"] > 0
        ):
            bvps = (
                row["equity_capital"] +
                row["reserves"]
            ) / row["equity_capital"]
        else:
            bvps = None

        results.append({

            "company_id": row["company_id"],

            "year": row["year_pnl"],

            "net_profit_margin_pct": npm,

            "operating_profit_margin_pct": opm,

            "return_on_equity_pct": roe,

            "debt_to_equity": de_ratio,

            "interest_coverage": icr,

            "icr_label": label,

            "asset_turnover": at,

            "free_cash_flow_cr": fcf,

            "cash_from_operations_cr": cfo,

            "capex_cr": capex,

            "earnings_per_share": row["eps"],

            "book_value_per_share": bvps,

            "dividend_payout_ratio_pct":
                row["dividend_payout"],

            "total_debt_cr":
                row["borrowings"],

            "market_cap_crore":
                row["market_cap_crore"],

            "pe_ratio":
                row["pe_ratio"],

            "pb_ratio":
                row["pb_ratio"],

            "dividend_yield_pct":
                row["dividend_yield_pct"],

            # Placeholder until full CAGR engine integration
            "revenue_cagr_5yr": None,

            "pat_cagr_5yr": None,

            "eps_cagr_5yr": None,

            # Placeholder until Day 17
            "composite_quality_score": None

        })

    ratio_df = pd.DataFrame(results)

    conn = sqlite3.connect(DB_PATH)

    ratio_df.to_sql(
        "financial_ratios",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("=" * 60)
    print(f"Loaded {len(ratio_df)} ratio rows")
    print("financial_ratios table updated successfully.")
    print("=" * 60)

    return ratio_df

if __name__ == "__main__":
   generate_financial_ratios()