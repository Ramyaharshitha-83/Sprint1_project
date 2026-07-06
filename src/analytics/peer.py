import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"


def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            net_profit_margin_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr,
            composite_quality_score
        FROM financial_ratios
        """,
        conn
    )

    peers = pd.read_sql(
        """
        SELECT
            peer_group_name,
            company_id,
            is_benchmark
        FROM peer_groups
        """,
        conn
    )

    conn.close()

    return ratios, peers


def calculate_percentiles():

    ratios, peers = load_data()

    df = pd.merge(
        ratios,
        peers,
        on="company_id",
        how="left"
    )

    df = df[
        df["peer_group_name"].notna()
    ].copy()

    metrics = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]

    records = []

    for group in sorted(df["peer_group_name"].unique()):

        peer_df = df[
            df["peer_group_name"] == group
        ].copy()

        for metric in metrics:

            if metric not in peer_df.columns:
                continue

            values = pd.to_numeric(
                peer_df[metric],
                errors="coerce"
            )

            if values.notna().sum() == 0:
                continue

            ascending = (
                metric == "debt_to_equity"
            )

            ranks = values.rank(
                pct=True,
                ascending=ascending
            )

            if metric == "debt_to_equity":
                ranks = 1 - ranks

            for idx, row in peer_df.iterrows():

                records.append({

                    "company_id":
                        row["company_id"],

                    "peer_group_name":
                        row["peer_group_name"],

                    "year":
                        row["year"],

                    "metric":
                        metric,

                    "value":
                        row[metric],

                    "percentile_rank":
                        round(
                            ranks.loc[idx] * 100,
                            2
                        )

                })

    result = pd.DataFrame(records)

    return result

def save_to_database(df):

    conn = sqlite3.connect(DB_PATH)

    df.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("=" * 60)
    print("Peer Percentiles Saved")
    print("=" * 60)
    print(f"Rows Written : {len(df)}")


if __name__ == "__main__":

    df = calculate_percentiles()

    print("=" * 60)
    print("Peer Percentiles Generated")
    print("=" * 60)

    print(df.head())

    print()

    print("Total Rows:", len(df))

    save_to_database(df)