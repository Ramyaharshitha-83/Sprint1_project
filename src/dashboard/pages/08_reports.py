import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql("""
        SELECT
            id,
            company_name,
            bse_profile
        FROM companies
    """, conn)

    conn.close()

    companies.rename(
        columns={"id": "company_id"},
        inplace=True
    )

    return companies


companies = load_data()

st.title("📄 Annual Reports")

ticker = st.selectbox(
    "Select Company",
    sorted(companies["company_id"])
)

company = companies[
    companies["company_id"] == ticker
].iloc[0]

st.subheader(company["company_name"])

years = list(range(2014, 2025))

report_df = pd.DataFrame({
    "Year": years,
    "Annual Report": [
        f"{company['bse_profile']}"
        for _ in years
    ]
})

st.dataframe(
    report_df,
    use_container_width=True
)

st.markdown("### Report Links")

for year in years:

    url = company["bse_profile"]

    if pd.notna(url) and str(url).startswith("http"):

        st.markdown(
            f"✅ **{year}** - [Open Report]({url})"
        )

    else:

        st.error(
            f"{year} : Report Unavailable"
        )