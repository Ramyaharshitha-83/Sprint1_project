import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    companies = pd.read_sql(
        "SELECT id, company_name FROM companies",
        conn
    )

    sectors = pd.read_sql(
        "SELECT company_id, broad_sector FROM sectors",
        conn
    )

    conn.close()

    companies.rename(
        columns={"id": "company_id"},
        inplace=True
    )

    df = ratios.merge(
        companies,
        on="company_id",
        how="left"
    )

    df = df.merge(
        sectors,
        on="company_id",
        how="left"
    )

    return df


df = load_data()

st.title("📊 Financial Screener")

# ----------------------------------------------------
# Year Filter
# ----------------------------------------------------
years = [
    y for y in sorted(df["year"].dropna().unique().tolist())
    if y.startswith("Mar") or y == "TTM"
]

# Prefer latest complete financial year
default_year = "Mar 2024"

if default_year in years:
    default_index = years.index(default_year)
else:
    default_index = len(years) - 1

selected_year = st.sidebar.selectbox(
    "Year",
    years,
    index=default_index
)

screen = df[
    df["year"] == selected_year
].copy()

# ----------------------------------------------------
# Presets
# ----------------------------------------------------

st.sidebar.header("Preset Screener")

preset = st.sidebar.selectbox(
    "Choose Preset",
    [
        "Custom",
        "Quality Compounder",
        "Value Pick",
        "Growth Accelerator",
        "Dividend Champion",
        "Debt Free Blue Chip",
        "Turnaround Watch"
    ]
)

# Default values
roe = 0.0
de = 10.0
asset = 0.0
pe = 500.0
pb = 100.0
dividend = 0.0

if preset == "Quality Compounder":
    roe = 15
    de = 1

elif preset == "Value Pick":
    pe = 20
    pb = 3
    de = 2

elif preset == "Growth Accelerator":
    roe = 20
    de = 2

elif preset == "Dividend Champion":
    dividend = 2

elif preset == "Debt Free Blue Chip":
    roe = 12
    de = 0

elif preset == "Turnaround Watch":
    roe = 10

# ----------------------------------------------------
# Filters
# ----------------------------------------------------

st.sidebar.header("Custom Filters")

roe = st.sidebar.slider(
    "Minimum ROE",
    0.0,
    100.0,
    float(roe)
)

de = st.sidebar.slider(
    "Maximum Debt / Equity",
    0.0,
    10.0,
    float(de)
)

asset = st.sidebar.slider(
    "Minimum Asset Turnover",
    0.0,
    5.0,
    float(asset)
)

pe = st.sidebar.slider(
    "Maximum P/E",
    0.0,
    500.0,
    float(pe)
)

pb = st.sidebar.slider(
    "Maximum P/B",
    0.0,
    100.0,
    float(pb)
)

dividend = st.sidebar.slider(
    "Minimum Dividend Yield",
    0.0,
    10.0,
    float(dividend)
)

# ----------------------------------------------------
# Apply Filters
# ----------------------------------------------------

if "return_on_equity_pct" in screen.columns:
    screen = screen[
        screen["return_on_equity_pct"].fillna(0) >= roe
    ]

if "debt_to_equity" in screen.columns:
    screen = screen[
        screen["debt_to_equity"].fillna(999) <= de
    ]

if "asset_turnover" in screen.columns:
    screen = screen[
        screen["asset_turnover"].fillna(0) >= asset
    ]

if "pe_ratio" in screen.columns:
    screen = screen[
        screen["pe_ratio"].fillna(0) <= pe
    ]

if "pb_ratio" in screen.columns:
    screen = screen[
        screen["pb_ratio"].fillna(0) <= pb
    ]

if "dividend_yield_pct" in screen.columns:
    screen = screen[
        screen["dividend_yield_pct"].fillna(0) >= dividend
    ]

# ----------------------------------------------------
# Sort
# ----------------------------------------------------

if "composite_quality_score" in screen.columns:

    screen["composite_quality_score"] = pd.to_numeric(
        screen["composite_quality_score"],
        errors="coerce"
    )

    screen = screen.sort_values(
        by="composite_quality_score",
        ascending=False,
        na_position="last"
    )

# ----------------------------------------------------
# Result Count
# ----------------------------------------------------

st.subheader(
    f"📈 {len(screen)} Companies Match"
)

# ----------------------------------------------------
# Display Table
# ----------------------------------------------------

columns = [
    "company_id",
    "company_name",
    "broad_sector",
    "return_on_equity_pct",
    "debt_to_equity",
    "asset_turnover",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "composite_quality_score"
]

available_columns = [
    col for col in columns
    if col in screen.columns
]

st.dataframe(
    screen[available_columns],
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------------------
# CSV Download
# ----------------------------------------------------

csv = screen.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download CSV",
    data=csv,
    file_name="screener_output.csv",
    mime="text/csv"
)