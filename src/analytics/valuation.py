import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "output"


def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        """,
        conn
    )

    companies = pd.read_sql(
        """
        SELECT
            id,
            company_name
        FROM companies
        """,
        conn
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector,
            sub_sector
        FROM sectors
        """,
        conn
    )

    

    conn.close()

    companies.rename(
        columns={
            "id": "company_id"
        },
        inplace=True
    )

    return ratios, companies, sectors


def prepare_dataframe():

    ratios, companies, sectors = load_data()

    # -----------------------------
    # Latest complete financial year
    # -----------------------------
    latest = ratios[
        ratios["year"] == "Mar 2024"
    ].copy()

    # fallback if unavailable
    if latest.empty:

        latest_year = (
            ratios.groupby("year")["company_id"]
            .nunique()
            .sort_values(ascending=False)
            .index[0]
        )

        latest = ratios[
            ratios["year"] == latest_year
        ].copy()

    # -----------------------------
    # Merge tables
    # -----------------------------
    df = latest.merge(
        companies,
        on="company_id",
        how="left"
    )
    
    df = df.merge(
        sectors,
        on="company_id",
        how="left"
    )

    
  
    # -----------------------------
    # Numeric conversion
    # -----------------------------
    numeric_cols = [
        "free_cash_flow_cr",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda"
    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # -----------------------------
    # Fill missing values
    # -----------------------------
    df["market_cap_crore"] = (
        df["market_cap_crore"]
        .replace(0, np.nan)
    )

    df["free_cash_flow_cr"] = (
        df["free_cash_flow_cr"]
        .fillna(0)
    )

    return df
    # --------------------------------------------------
# Valuation Calculations
# --------------------------------------------------

def calculate_valuation(df):

    # ------------------------------------
    # FCF Yield %
    # ------------------------------------

    df["fcf_yield_pct"] = (
        df["free_cash_flow_cr"] /
        df["market_cap_crore"]
    ) * 100

    df["fcf_yield_pct"] = (
        df["fcf_yield_pct"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # ------------------------------------
    # Sector Median P/E
    # ------------------------------------

    sector_pe = (
    df.groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
    .rename(
        columns={
            "pe_ratio": "sector_median_pe"
            }
        )
    )

    df = df.merge(
        sector_pe,
        on="broad_sector",
        how="left"
    )

   


    # ------------------------------------
    # PE vs Sector Median %
    # ------------------------------------

    df["pe_vs_sector_median_pct"] = (
        (
            df["pe_ratio"] -
            df["sector_median_pe"]
        )
        /
        df["sector_median_pe"]
    ) * 100

    df["pe_vs_sector_median_pct"] = (
        df["pe_vs_sector_median_pct"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # ------------------------------------
    # Valuation Flag
    # ------------------------------------

    def valuation_flag(row):

        pe = row["pe_ratio"]
        median = row["sector_median_pe"]

        if pd.isna(pe) or pd.isna(median):
            return "Fair"

        if pe > median * 1.5:
            return "Caution"

        elif pe < median * 0.7:
            return "Discount"

        else:
            return "Fair"

    df["flag"] = df.apply(
        valuation_flag,
        axis=1
    )

    # ------------------------------------
    # Keep Required Columns
    # ------------------------------------

    required = [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "market_cap_crore",
        "free_cash_flow_cr",
        "fcf_yield_pct",
        "sector_median_pe",
        "pe_vs_sector_median_pct",
        "flag"
    ]

    available = [
        c for c in required
        if c in df.columns
    ]

    df = df[available].copy()

    # ------------------------------------
    # Round Numeric Columns
    # ------------------------------------

    numeric_cols = df.select_dtypes(
        include=["float64", "int64"]
    ).columns

    df[numeric_cols] = (
        df[numeric_cols]
        .round(2)
    )

    return df
    # --------------------------------------------------
# Export Files
# --------------------------------------------------

def export_results(df):

    Path(OUTPUT_DIR).mkdir(
        exist_ok=True
    )

    summary_path = (
        Path(OUTPUT_DIR)
        / "valuation_summary.xlsx"
    )

    flags_path = (
        Path(OUTPUT_DIR)
        / "valuation_flags.csv"
    )

    # ------------------------------------
    # Sort by FCF Yield
    # ------------------------------------

    df = df.sort_values(
        by="fcf_yield_pct",
        ascending=False
    )

    # ------------------------------------
    # Excel Summary
    # ------------------------------------

    with pd.ExcelWriter(
        summary_path,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Valuation Summary"
        )

    # ------------------------------------
    # Flags CSV
    # ------------------------------------

    flagged = df[
        df["flag"].isin(
            [
                "Discount",
                "Caution"
            ]
        )
    ].copy()

    flagged.to_csv(
        flags_path,
        index=False
    )

    return summary_path, flags_path, flagged


# --------------------------------------------------
# Terminal Summary
# --------------------------------------------------

def print_summary(
    df,
    flagged,
    summary_path,
    flags_path
):

    print("=" * 55)
    print("Valuation Summary Generated")
    print("=" * 55)

    print(
        f"Companies Processed : {len(df)}"
    )

    print()

    print(
        f"Fair      : {(df['flag']=='Fair').sum()}"
    )

    print(
        f"Discount  : {(df['flag']=='Discount').sum()}"
    )

    print(
        f"Caution   : {(df['flag']=='Caution').sum()}"
    )

    print()

    print(
        f"Flagged Companies : {len(flagged)}"
    )

    print()

    print("Files Created")

    print(
        f"✓ {summary_path}"
    )

    print(
        f"✓ {flags_path}"
    )
    # --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    try:

        # Prepare Data
        df = prepare_dataframe()

        # Calculate Valuation
        valuation_df = calculate_valuation(df)

        # Export Files
        summary_path, flags_path, flagged = export_results(
            valuation_df
        )

        # Print Summary
        print_summary(
            valuation_df,
            flagged,
            summary_path,
            flags_path
        )

    except Exception as e:

        print("=" * 55)
        print("Valuation Engine Failed")
        print("=" * 55)
        print(e)


if __name__ == "__main__":
    main()