import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

DB_PATH = "data/nifty100.db"


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            free_cash_flow_cr,
            capex_cr,
            dividend_payout_ratio_pct,
            debt_to_equity,
            cash_from_operations_cr
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

    return df


df = load_data()

latest_year = (
    df["year"]
    .dropna()
    .value_counts()
    .idxmax()
)

df = df[
    df["year"] == latest_year
].copy()


def classify(row):

    fcf = row.get("free_cash_flow_cr", 0) or 0
    capex = row.get("capex_cr", 0) or 0
    payout = row.get("dividend_payout_ratio_pct", 0) or 0
    debt = row.get("debt_to_equity", 0) or 0

    if debt == 0:
        return "Debt Free"

    if payout > 60:
        return "Dividend Champion"

    if capex > fcf:
        return "Aggressive Expansion"

    if fcf > 0 and debt < 1:
        return "Cash Generator"

    if debt > 2:
        return "Highly Leveraged"

    if fcf < 0:
        return "Cash Burn"

    if payout == 0:
        return "Reinvestment"

    return "Balanced"


df["capital_pattern"] = df.apply(
    classify,
    axis=1
)

st.title("🌳 Capital Allocation Map")

st.write(df.shape)
st.write(df.head())

df["cash_from_operations_cr"] = (
    pd.to_numeric(
        df["cash_from_operations_cr"],
        errors="coerce"
    )
    .fillna(1)
)

df = df[
    df["cash_from_operations_cr"] > 0
]

fig = px.treemap(
    df,
    path=["capital_pattern", "company_id"],
    values="cash_from_operations_cr",
    color="capital_pattern",
    hover_data=[
        "company_name",
        "free_cash_flow_cr",
        "debt_to_equity"
    ]
)

fig.update_layout(
    height=700,
    margin=dict(t=40, l=10, r=10, b=10)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

pattern = st.selectbox(
    "Select Pattern",
    sorted(df["capital_pattern"].unique())
)

st.subheader(pattern)

st.dataframe(
    df[
        df["capital_pattern"] == pattern
    ][
        [
            "company_id",
            "company_name",
            "free_cash_flow_cr",
            "capex_cr",
            "dividend_payout_ratio_pct",
            "debt_to_equity"
        ]
    ],
    use_container_width=True
)