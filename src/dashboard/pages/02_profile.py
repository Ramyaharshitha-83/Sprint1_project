import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

DB_PATH = "data/nifty100.db"


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    pnl = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn
    )

    pros = pd.read_sql(
        "SELECT * FROM prosandcons",
        conn
    )

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn
    )

    conn.close()

    return companies, ratios, pnl, pros, sectors


companies, ratios, pnl, pros, sectors = load_data()

st.title("🏢 Company Profile")

# ----------------------------------------------------
# Company Selection
# ----------------------------------------------------

company_list = sorted(companies["id"].unique())

ticker = st.selectbox(
    "Select Company",
    company_list
)

company = companies[
    companies["id"] == ticker
]

if company.empty:
    st.warning("Ticker not found.")
    st.stop()

company = company.iloc[0]

sector = sectors[
    sectors["company_id"] == ticker
]

# ----------------------------------------------------
# Latest Ratios (Ignore TTM)
# ----------------------------------------------------

latest = ratios[
    (ratios["company_id"] == ticker) &
    (ratios["year"] != "TTM")
]

if not latest.empty:
    latest = latest.iloc[-1]

history = pnl[
    pnl["company_id"] == ticker
]

# ----------------------------------------------------
# Header
# ----------------------------------------------------

st.subheader(company["company_name"])

left, right = st.columns(2)

with left:

    st.write("**Ticker:**", company["id"])

    if not sector.empty:

        st.write(
            "**Sector:**",
            sector.iloc[0]["broad_sector"]
        )

        st.write(
            "**Sub Sector:**",
            sector.iloc[0]["sub_sector"]
        )

with right:

    st.write(
        "**Website:**",
        company["website"]
    )

    st.write(
        "**Book Value:**",
        company["book_value"]
    )

    st.write(
        "**Face Value:**",
        company["face_value"]
    )

st.divider()

# ----------------------------------------------------
# KPI Cards
# ----------------------------------------------------

if not latest.empty:

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "ROE",
            f"{latest['return_on_equity_pct']:.2f}%"
        )

    with c2:

        st.metric(
            "Net Profit Margin",
            f"{latest['net_profit_margin_pct']:.2f}%"
        )

    with c3:

        st.metric(
            "Debt / Equity",
            f"{latest['debt_to_equity']:.2f}"
        )

    c4, c5, c6 = st.columns(3)

    with c4:

        st.metric(
            "Asset Turnover",
            f"{latest['asset_turnover']:.2f}"
        )

    with c5:

        st.metric(
            "EPS",
            f"{latest['earnings_per_share']:.2f}"
        )

    with c6:

        st.metric(
            "Dividend Payout",
            f"{latest['dividend_payout_ratio_pct']:.2f}%"
        )

st.divider()

# ----------------------------------------------------
# Revenue vs Net Profit
# ----------------------------------------------------

st.subheader("Revenue vs Net Profit")

if not history.empty:

    fig = px.bar(
        history,
        x="year",
        y=["sales", "net_profit"],
        barmode="group",
        title="Revenue vs Net Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.info("No Revenue History Available.")

# ----------------------------------------------------
# ROE Trend
# ----------------------------------------------------

st.subheader("ROE Trend")

roe_history = ratios[
    (ratios["company_id"] == ticker) &
    (ratios["year"] != "TTM")
]

if not roe_history.empty:

    fig = px.line(
        roe_history,
        x="year",
        y="return_on_equity_pct",
        markers=True,
        title="Return on Equity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ----------------------------------------------------
# About Company
# ----------------------------------------------------

st.subheader("About Company")

st.write(
    company["about_company"]
)

st.divider()

# ----------------------------------------------------
# Pros & Cons
# ----------------------------------------------------

st.subheader("Pros & Cons")

pc = pros[
    pros["company_id"] == ticker
]

if not pc.empty:

    left, right = st.columns(2)

    with left:

        st.markdown("### ✅ Pros")

        for p in pc["pros"].dropna():

            st.success(p)

    with right:

        st.markdown("### ❌ Cons")

        for c in pc["cons"].dropna():

            st.error(c)

else:

    st.info("No Pros & Cons Available.")