import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

DB_PATH = "data/nifty100.db"


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    pnl = pd.read_sql(
        "SELECT company_id, year, sales FROM profitandloss",
        conn
    )

    sectors = pd.read_sql(
        "SELECT company_id, broad_sector, sub_sector FROM sectors",
        conn
    )

    market = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            market_cap_crore
        FROM market_cap
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

    return ratios, pnl, sectors, market, companies


ratios, pnl, sectors, market, companies = load_data()

st.title("🏭 Sector Analysis")

# -------------------------------------------------
# Latest Annual Data
# -------------------------------------------------

ratios = ratios[
    ratios["year"] == "Mar 2024"
]

pnl = pnl[
    pnl["year"] == "Mar 2024"
]

market = market[
    market["year"] == 2024
]

df = (
    ratios
    .merge(pnl, on=["company_id", "year"], how="left")
    .merge(sectors, on="company_id", how="left")
    .merge(market, on="company_id", how="left")
    .merge(companies, on="company_id", how="left")
)

df["market_cap_crore"] = (
    df["market_cap_crore_x"]
    .fillna(df["market_cap_crore_y"])
)
# -------------------------------------------------
# Sector Filter
# -------------------------------------------------

sector_list = sorted(
    df["broad_sector"].dropna().unique()
)

selected_sector = st.sidebar.selectbox(
    "Select Sector",
    sector_list
)

sector_df = df[
    df["broad_sector"] == selected_sector
].copy()

# -------------------------------------------------
# Bubble Chart
# -------------------------------------------------

st.subheader("Sector Bubble Chart")

fig = px.scatter(
    sector_df,
    x="sales",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_name",
    text="company_id",
    title=f"{selected_sector} Companies"
)

fig.update_traces(
    textposition="top center"
)

fig.update_layout(
    height=700
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -------------------------------------------------
# Sector Median KPI
# -------------------------------------------------

st.subheader("Sector Median KPIs")

metrics = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "asset_turnover",
    "debt_to_equity"
]

median_df = (
    sector_df[metrics]
    .median()
    .reset_index()
)

median_df.columns = [
    "Metric",
    "Median"
]

bar = px.bar(
    median_df,
    x="Metric",
    y="Median",
    text="Median",
    title=f"{selected_sector} Median KPIs"
)

bar.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

bar.update_layout(
    height=500
)

st.plotly_chart(
    bar,
    use_container_width=True
)

# -------------------------------------------------
# Company Table
# -------------------------------------------------

st.subheader("Companies in Sector")

cols = [
    "company_id",
    "company_name",
    "sub_sector",
    "sales",
    "return_on_equity_pct",
    "market_cap_crore"
]

st.dataframe(
    sector_df[cols],
    hide_index=True,
    use_container_width=True,
    height=450
)

st.subheader("Sector Median KPIs")

median_df = pd.DataFrame({
    "Metric": [
        "ROE",
        "Net Profit Margin",
        "Asset Turnover",
        "Debt/Equity"
    ],
    "Value": [
        sector_df["return_on_equity_pct"].median(),
        sector_df["net_profit_margin_pct"].median(),
        sector_df["asset_turnover"].median(),
        sector_df["debt_to_equity"].median()
    ]
})

fig = px.bar(
    median_df,
    x="Metric",
    y="Value",
    text="Value",
    title=f"{selected_sector} Median KPIs"
)

fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")

st.plotly_chart(fig, use_container_width=True)