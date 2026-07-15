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

    sectors = pd.read_sql(
        "SELECT * FROM sectors",
        conn
    )

    market = pd.read_sql(
        "SELECT * FROM market_cap",
        conn
    )

    conn.close()

    return ratios, sectors, market


st.title("🏠 Home Dashboard")

ratios, sectors, market = load_data()

# ------------------------------------
# Sidebar Year Filter
# ------------------------------------

years = sorted(
    ratios["year"].dropna().unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years) - 1
)

filtered = ratios[
    ratios["year"] == selected_year
].copy()

# ------------------------------------
# KPI Cards
# ------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average ROE",
        f"{filtered['return_on_equity_pct'].mean():.2f}%"
    )

with col2:
    st.metric(
        "Median D/E",
        f"{filtered['debt_to_equity'].median():.2f}"
    )

with col3:
    st.metric(
        "Total Companies",
        filtered["company_id"].nunique()
    )

col4, col5, col6 = st.columns(3)

market_year = market[
    market["year"] == 2024
]

with col4:

    if not market_year.empty:
        st.metric(
            "Median P/E",
            f"{market_year['pe_ratio'].median():.2f}"
        )
    else:
        st.metric(
            "Median P/E",
            "N/A"
        )

with col5:

    if "revenue_cagr_5yr" in filtered.columns:

        values = pd.to_numeric(
            filtered["revenue_cagr_5yr"],
            errors="coerce"
        )

        median = values.median()

        if pd.isna(median):
            st.metric(
                "Median Revenue CAGR",
                "N/A"
            )
        else:
            st.metric(
                "Median Revenue CAGR",
                f"{median:.2f}%"
            )

    else:

        st.metric(
            "Median Revenue CAGR",
            "N/A"
        )

with col6:

    debt_free = (
        filtered["debt_to_equity"] == 0
    ).sum()

    st.metric(
        "Debt Free Companies",
        debt_free
    )

st.divider()

# ------------------------------------
# Sector Distribution
# ------------------------------------

st.subheader("Sector Distribution")

sector_counts = (
    sectors.groupby("broad_sector")
    .size()
    .reset_index(name="Companies")
)

fig = px.pie(
    sector_counts,
    names="broad_sector",
    values="Companies",
    hole=0.45,
    title="Companies by Sector"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ------------------------------------
# Top 5 Companies
# ------------------------------------

st.subheader("Top 5 Companies by Composite Score")

if "composite_quality_score" in filtered.columns:

    temp = filtered.copy()

    temp["composite_quality_score"] = pd.to_numeric(
        temp["composite_quality_score"],
        errors="coerce"
    )

    top5 = (
        temp.sort_values(
            "composite_quality_score",
            ascending=False
        )
        [["company_id", "composite_quality_score"]]
        .head(5)
    )

    st.dataframe(
        top5,
        use_container_width=True
    )

else:

    st.info(
        "Composite score not available."
    )