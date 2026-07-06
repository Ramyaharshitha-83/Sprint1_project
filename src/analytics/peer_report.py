import sqlite3
import pandas as pd
import os

DB_PATH = "data/nifty100.db"


def load_data():

    conn = sqlite3.connect(DB_PATH)

    peer_groups = pd.read_sql(
        "SELECT * FROM peer_groups",
        conn
    )

    peer_percentiles = pd.read_sql(
        "SELECT * FROM peer_percentiles",
        conn
    )

    financial_ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    return (
        peer_groups,
        peer_percentiles,
        financial_ratios
    )


def generate_report():

    (
        peer_groups,
        peer_percentiles,
        financial_ratios
    ) = load_data()

    os.makedirs(
        "output",
        exist_ok=True
    )

    output_file = "output/peer_comparison.xlsx"

    with pd.ExcelWriter(output_file) as writer:

        groups = sorted(
            peer_groups["peer_group_name"].unique()
        )

        for group in groups:

            companies = peer_groups[
                peer_groups["peer_group_name"] == group
            ]

            merged = financial_ratios.merge(
                companies[
                    [
                        "company_id",
                        "is_benchmark"
                    ]
                ],
                on="company_id",
                how="inner"
            )

            percentile = peer_percentiles[
                peer_percentiles[
                    "peer_group_name"
                ] == group
            ]

            sheet = merged.merge(
                percentile[
                    [
                        "company_id",
                        "metric",
                        "percentile_rank"
                    ]
                ],
                on="company_id",
                how="left"
            )

            sheet.to_excel(
                writer,
                sheet_name=group[:31],
                index=False
            )

    print("=" * 60)
    print("Peer Comparison Report Generated")
    print("=" * 60)
    print("Output :", output_file)
    print(
        "Peer Groups :",
        len(groups)
    )


if __name__ == "__main__":

    generate_report()