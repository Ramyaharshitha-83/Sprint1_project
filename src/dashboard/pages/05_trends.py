import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

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

    conn.close()

    companies.rename(
        columns={"id": "company_id"},
        inplace=True
    )

    return ratios, companies


ratios, companies = load_data()

st.title("📈 Trend Analysis")

company_list = sorted(companies["company_id"].unique())

ticker = st.selectbox(
    "Select Company",
    company_list
)

history = ratios[
    ratios["company_id"] == ticker
].copy()

history = history[
    history["year"].str.startswith("Mar")
]

history = history.sort_values("year")

metrics = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "asset_turnover",
    "debt_to_equity",
    "earnings_per_share",
    "free_cash_flow_cr",
    "book_value_per_share"
]

available = [
    m for m in metrics
    if m in history.columns
]

selected = st.multiselect(
    "Select up to 3 Metrics",
    available,
    default=available[:2],
    max_selections=3
)

fig = go.Figure()

for metric in selected:

    values = pd.to_numeric(
        history[metric],
        errors="coerce"
    )

    fig.add_trace(
        go.Scatter(
            x=history["year"],
            y=values,
            mode="lines+markers+text",
            name=metric,
            text=[
                ""
                if pd.isna(v)
                else (
                    ""
                    if i == 0 or pd.isna(values.iloc[i - 1]) or values.iloc[i - 1] == 0
                    else f"{((v-values.iloc[i-1])/values.iloc[i-1]*100):.1f}%"
                )
                for i, v in enumerate(values)
            ],
            textposition="top center"
        )
    )

fig.update_layout(
    height=650,
    xaxis_title="Year",
    yaxis_title="Value",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)