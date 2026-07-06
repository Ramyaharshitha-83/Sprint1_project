import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

DB_PATH = "data/nifty100.db"


def load_data():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            net_profit_margin_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            dividend_yield_pct,
            composite_quality_score
        FROM financial_ratios
    """, conn)

    conn.close()

    return df


def normalize(series):

    series = pd.to_numeric(series, errors="coerce").fillna(0)

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series([50] * len(series), index=series.index)

    return ((series - minimum) / (maximum - minimum)) * 100


def prepare_dataframe(df):

    metrics = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "dividend_yield_pct",
        "composite_quality_score"
    ]

    for metric in metrics:

        if metric == "debt_to_equity":
            df[metric] = 100 - normalize(df[metric])
        else:
            df[metric] = normalize(df[metric])

    return df


def create_radar(values, labels, title, output_file):

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    values = values.tolist()

    values += values[:1]
    angles += angles[:1]

    fig = plt.figure(figsize=(6, 6))

    ax = plt.subplot(111, polar=True)

    ax.plot(angles, values, linewidth=2)

    ax.fill(angles, values, alpha=0.25)

    ax.set_xticks(angles[:-1])

    ax.set_xticklabels(labels, fontsize=8)

    ax.set_title(title)

    plt.savefig(output_file)

    plt.close()

def generate_all_charts():

    df = load_data()

    df = prepare_dataframe(df)

    os.makedirs(
        "reports/radar_charts",
        exist_ok=True
    )

    metrics = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "dividend_yield_pct",
        "composite_quality_score"
    ]

    labels = [
        "ROE",
        "NPM",
        "D/E",
        "ICR",
        "Asset Turnover",
        "FCF",
        "Dividend",
        "Score"
    ]

    latest = (
        df.sort_values("year")
          .groupby("company_id")
          .tail(1)
    )

    count = 0

    for _, row in latest.iterrows():

        values = row[metrics].fillna(0)

        output_file = (
            f"reports/radar_charts/"
            f"{row['company_id']}_radar.png"
        )

        create_radar(
            values,
            labels,
            row["company_id"],
            output_file
        )

        count += 1

    print("=" * 60)
    print("Radar Charts Generated")
    print("=" * 60)
    print(f"Charts Created : {count}")

if __name__ == "__main__":

    generate_all_charts()