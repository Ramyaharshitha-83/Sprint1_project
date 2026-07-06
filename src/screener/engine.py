import sqlite3
import pandas as pd
import yaml

DB_PATH = "data/nifty100.db"


def load_config():
    with open("config/screener_config.yaml", "r") as file:
        return yaml.safe_load(file)


def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    sectors = pd.read_sql(
        "SELECT company_id,broad_sector FROM sectors",
        conn
    )

    conn.close()

    return ratios.merge(
        sectors,
        on="company_id",
        how="left"
    )


def apply_filters(df, config):

    filters = config["filters"]

    if "return_on_equity_pct" in df.columns:
        df = df[
            df["return_on_equity_pct"] >= filters["roe_min"]
        ]

    if "debt_to_equity" in df.columns:

        financial_mask = (
            df["broad_sector"] == "Financials"
        )

        debt_mask = (
            df["debt_to_equity"] <=
            filters["debt_to_equity_max"]
        )

        df = df[
            financial_mask | debt_mask
        ]

    if "asset_turnover" in df.columns:
        df = df[
            df["asset_turnover"] >=
            filters["asset_turnover_min"]
        ]

    df["composite_quality_score"] = (
        df["return_on_equity_pct"].fillna(0)
    )

    return df.sort_values(
        "composite_quality_score",
        ascending=False
    )

def calculate_composite_score(df):

    df = df.copy()

    def norm(series):

        series = series.fillna(0)

        minimum = series.min()
        maximum = series.max()

        if maximum == minimum:
            return pd.Series([50] * len(series), index=series.index)

        return (
            (series - minimum)
            / (maximum - minimum)
        ) * 100

    roe = norm(df["return_on_equity_pct"])

    fcf = norm(df["free_cash_flow_cr"])

    asset = norm(df["asset_turnover"])

    leverage = 100 - norm(df["debt_to_equity"])

    df["composite_quality_score"] = (

        roe * 0.35 +

        fcf * 0.30 +

        asset * 0.20 +

        leverage * 0.15

    ).round(2)

    return df
# ------------------------
# PRESET SCREENERS
# ------------------------

def quality_compounder(df):

    if "free_cash_flow_cr" not in df.columns:
        return pd.DataFrame()

    return df[
        (df["return_on_equity_pct"] > 15) &
        (df["debt_to_equity"] < 1) &
        (df["free_cash_flow_cr"] > 0)
    ]


def value_pick(df):

    required = [
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct"
    ]

    if not all(c in df.columns for c in required):
        return pd.DataFrame()

    return df[
        (df["pe_ratio"] < 20) &
        (df["pb_ratio"] < 3) &
        (df["dividend_yield_pct"] > 1)
    ]


def growth_accelerator(df):

    if "pat_cagr_5yr" not in df.columns:
        return pd.DataFrame()

    return df[
        df["debt_to_equity"] < 2
    ]


def dividend_champion(df):

    if "dividend_yield_pct" not in df.columns:
        return pd.DataFrame()

    return df[
        (df["dividend_yield_pct"] > 2) &
        (df["dividend_payout_ratio_pct"] < 80) &
        (df["free_cash_flow_cr"] > 0)
    ]


def debt_free_bluechip(df):

    return df[
        (df["debt_to_equity"] == 0) &
        (df["return_on_equity_pct"] > 12)
    ]


def turnaround_watch(df):

    if "free_cash_flow_cr" not in df.columns:
        return pd.DataFrame()

    return df[
        df["free_cash_flow_cr"] > 0
    ]


def show_result(title, df):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print("Companies Found:", len(df))

    if len(df):

        cols = [
            "company_id",
            "return_on_equity_pct",
            "debt_to_equity"
        ]

        print(df[cols].head())

def export_excel(results):

    import os

    os.makedirs("output", exist_ok=True)

    with pd.ExcelWriter(
        "output/screener_output.xlsx"
    ) as writer:

        for name, data in results.items():

            data.to_excel(
                writer,
                sheet_name=name[:31],
                index=False
            )

    print("\nExcel exported successfully.")

def main():

    config = load_config()

    df = load_data()

    screened = apply_filters(df, config)

    screened = calculate_composite_score(screened)

    presets = {

        "Quality Compounder":
            quality_compounder(screened),

        "Value Pick":
            value_pick(screened),

        "Growth Accelerator":
            growth_accelerator(screened),

        "Dividend Champion":
            dividend_champion(screened),

        "Debt-Free Blue Chip":
            debt_free_bluechip(screened),

        "Turnaround Watch":
            turnaround_watch(screened)

    }

    for name, result in presets.items():

        print("\n" + "=" * 60)

        print(name)

        print("=" * 60)

        print("Companies Found:", len(result))

        if len(result):

            print(

                result[
                    [
                        "company_id",
                        "return_on_equity_pct",
                        "debt_to_equity",
                        "composite_quality_score"
                    ]
                ].head()

            )

    export_excel(presets)

    print("\nDay 17 completed successfully.")

if __name__ == "__main__":
    main()