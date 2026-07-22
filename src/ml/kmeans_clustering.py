import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output"


def load_data():
    """
    Load financial ratios for clustering.
    """

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            net_profit_margin_pct,
            debt_to_equity,
            asset_turnover,
            pe_ratio,
            pb_ratio,
            dividend_yield_pct,
            free_cash_flow_cr
        FROM financial_ratios
        WHERE year='Mar 2024'
        """,
        conn,
    )

    conn.close()

    return df


def preprocess_data(df):
    """
    Preprocess financial data for clustering.
    """

    features = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "asset_turnover",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "free_cash_flow_cr",
    ]

    X = df[features].copy()

    # Replace infinite values with NaN
    X.replace([float("inf"), float("-inf")], pd.NA, inplace=True)

    # Fill missing values using median
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X)

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    return X_scaled, features


def perform_clustering(df, X_scaled):
    """
    Train KMeans model and assign cluster labels.
    """

    Path(OUTPUT_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------
    # Elbow Method
    # -----------------------------

    inertia = []

    for k in range(1, 11):

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        model.fit(X_scaled)

        inertia.append(model.inertia_)

    plt.figure(figsize=(8, 5))

    plt.plot(
        range(1, 11),
        inertia,
        marker="o"
    )

    plt.title("Elbow Method")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Inertia")

    elbow_path = (
        Path(OUTPUT_DIR)
        / "elbow_plot.png"
    )

    plt.savefig(
        elbow_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # -----------------------------
    # Final KMeans (5 Clusters)
    # -----------------------------

    kmeans = KMeans(
        n_clusters=5,
        random_state=42,
        n_init=10
    )

    df["cluster"] = kmeans.fit_predict(X_scaled)

    output_file = (
        Path(OUTPUT_DIR)
        / "cluster_labels.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    return output_file, elbow_path, kmeans


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    df = load_data()

    X_scaled, features = preprocess_data(df)

    output_file, elbow_path, kmeans = perform_clustering(
        df,
        X_scaled
    )

    print("=" * 60)
    print("KMEANS CLUSTERING")
    print("=" * 60)
    print(f"Companies Clustered : {len(df)}")
    print(f"Features Used       : {len(features)}")
    print(f"Clusters Created    : {kmeans.n_clusters}")
    print()
    print("Generated Files")
    print(f"✓ {output_file}")
    print(f"✓ {elbow_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()