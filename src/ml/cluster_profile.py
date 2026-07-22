import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output"


def load_data():
    """
    Load cluster labels and company information.
    """

    cluster_df = pd.read_csv(
        Path(OUTPUT_DIR) / "cluster_labels.csv"
    )

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector
        FROM companies c
        LEFT JOIN sectors s
        ON c.id = s.company_id
        """,
        conn,
    )

    conn.close()

    df = cluster_df.merge(
        companies,
        on="company_id",
        how="left"
    )

    return df


def generate_reports(df):
    """
    Generate cluster profiling reports.
    """
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # Cluster Summary
    # -----------------------------
    summary = (
        df.groupby("cluster")
        .agg(
            companies=("company_id", "count"),
            avg_roe=("return_on_equity_pct", "mean"),
            avg_margin=("net_profit_margin_pct", "mean"),
            avg_debt=("debt_to_equity", "mean"),
            avg_pe=("pe_ratio", "mean"),
            avg_pb=("pb_ratio", "mean"),
            avg_dividend=("dividend_yield_pct", "mean"),
            avg_fcf=("free_cash_flow_cr", "mean"),
        )
        .round(2)
        .reset_index()
    )

    # Assign cluster names
    cluster_names = {
        0: "High Growth",
        1: "Stable Performers",
        2: "Value Stocks",
        3: "Turnaround",
        4: "Outliers",
    }

    summary["cluster_name"] = summary["cluster"].map(cluster_names)

    summary.to_csv(
        Path(OUTPUT_DIR) / "cluster_summary.csv",
        index=False,
    )

    # -----------------------------
    # Correlation Heatmap
    # -----------------------------
    corr_columns = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "asset_turnover",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "free_cash_flow_cr",
    ]

    corr = df[corr_columns].corr()

    plt.figure(figsize=(8, 6))
    plt.imshow(corr, cmap="coolwarm", interpolation="nearest")
    plt.colorbar()

    plt.xticks(range(len(corr_columns)), corr_columns, rotation=90)
    plt.yticks(range(len(corr_columns)), corr_columns)

    plt.tight_layout()

    plt.savefig(
        Path(OUTPUT_DIR) / "correlation_heatmap.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    # -----------------------------
    # Outlier Report (IQR)
    # -----------------------------
    outliers = []

    for column in corr_columns:

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - (1.5 * iqr)
        upper = q3 + (1.5 * iqr)

        temp = df[
            (df[column] < lower) |
            (df[column] > upper)
        ][["company_id", column]].copy()

        temp["metric"] = column

        outliers.append(temp)

    outlier_df = pd.concat(outliers, ignore_index=True)

    outlier_df.to_csv(
        Path(OUTPUT_DIR) / "outlier_report.csv",
        index=False,
    )

    # -----------------------------
    # Portfolio Statistics
    # -----------------------------
    stats = df.describe(include="all").transpose()

    stats.to_csv(
        Path(OUTPUT_DIR) / "portfolio_statistics.csv"
    )

    return summary, outlier_df


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    df = load_data()

    summary, outliers = generate_reports(df)

    print("=" * 60)
    print("CLUSTER PROFILING")
    print("=" * 60)
    print(f"Companies Analysed : {len(df)}")
    print(f"Clusters           : {summary.shape[0]}")
    print(f"Outliers Found     : {len(outliers)}")
    print()
    print("Generated Files")
    print("✓ output/cluster_summary.csv")
    print("✓ output/correlation_heatmap.png")
    print("✓ output/outlier_report.csv")
    print("✓ output/portfolio_statistics.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()