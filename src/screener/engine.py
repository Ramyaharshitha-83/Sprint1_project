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
        "SELECT company_id, broad_sector FROM sectors",
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

    # ROE
    if "return_on_equity_pct" in df.columns:
        df = df[
            df["return_on_equity_pct"]
            >= filters["roe_min"]
        ]

    # Debt to Equity
    if "debt_to_equity" in df.columns:

        financials = df["broad_sector"] == "Financials"

        debt_ok = (
            df["debt_to_equity"]
            <= filters["debt_to_equity_max"]
        )

        df = df[
            financials | debt_ok
        ]

    # Asset Turnover
    if "asset_turnover" in df.columns:
        df = df[
            df["asset_turnover"]
            >= filters["asset_turnover_min"]
        ]

    # Placeholder composite score
    df["composite_quality_score"] = (
        df["return_on_equity_pct"]
        .fillna(0)
    )

    return df.sort_values(
        by="composite_quality_score",
        ascending=False
    )


def main():

    config = load_config()

    df = load_data()

    screened = apply_filters(
        df,
        config
    )

    print("\nTotal Companies After Filtering:")
    print(len(screened))

    print("\nTop Results:")
    print(
        screened[
            [
                "company_id",
                "return_on_equity_pct",
                "debt_to_equity",
                "composite_quality_score"
            ]
        ].head(10)
    )


if __name__ == "__main__":
    main()