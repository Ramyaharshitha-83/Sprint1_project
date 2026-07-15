import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "data/nifty100.db"


@st.cache_data(ttl=600)
def run_query(query, params=None):

    conn = sqlite3.connect(DB_PATH)

    if params:
        df = pd.read_sql(query, conn, params=params)
    else:
        df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_companies():
    return run_query("SELECT * FROM companies")


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    if year:

        return run_query(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id=?
            AND year=?
            """,
            (ticker, year)
        )

    return run_query(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
        """,
        (ticker,)
    )


@st.cache_data(ttl=600)
def get_pl(ticker):

    return run_query(
        "SELECT * FROM profitandloss WHERE company_id=?",
        (ticker,)
    )


@st.cache_data(ttl=600)
def get_bs(ticker):

    return run_query(
        "SELECT * FROM balancesheet WHERE company_id=?",
        (ticker,)
    )


@st.cache_data(ttl=600)
def get_cf(ticker):

    return run_query(
        "SELECT * FROM cashflow WHERE company_id=?",
        (ticker,)
    )


@st.cache_data(ttl=600)
def get_sectors():

    return run_query(
        "SELECT * FROM sectors"
    )


@st.cache_data(ttl=600)
def get_peers(group_name):

    return run_query(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name=?
        """,
        (group_name,)
    )


@st.cache_data(ttl=600)
def get_valuation(ticker):

    return run_query(
        """
        SELECT *
        FROM market_cap
        WHERE company_id=?
        """,
        (ticker,)
    )