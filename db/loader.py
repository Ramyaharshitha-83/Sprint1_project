import sqlite3
import pandas as pd

from src.etl.loader import load_core_dataset


DB_PATH = "data/nifty100.db"


def create_database():

    conn = sqlite3.connect(DB_PATH)

    with open("db/schema.sql", "r") as f:
        schema = f.read()

    conn.executescript(schema)

    conn.commit()

    return conn


def load_tables(conn):

    companies = load_core_dataset("companies.xlsx")
    profitandloss = load_core_dataset("profitandloss.xlsx")
    balancesheet = load_core_dataset("balancesheet.xlsx")
    cashflow = load_core_dataset("cashflow.xlsx")

    companies.to_sql(
        "companies",
        conn,
        if_exists="append",
        index=False
    )

    profitandloss.to_sql(
        "profitandloss",
        conn,
        if_exists="append",
        index=False
    )

    balancesheet.to_sql(
        "balancesheet",
        conn,
        if_exists="append",
        index=False
    )

    cashflow.to_sql(
        "cashflow",
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()


def verify_tables(conn):

    tables = [
        "companies",
        "profitandloss",
        "balancesheet",
        "cashflow"
    ]

    print("\nRow Counts\n")

    for table in tables:

        count = pd.read_sql_query(
            f"SELECT COUNT(*) AS cnt FROM {table}",
            conn
        )

        print(
            f"{table}: "
            f"{count['cnt'][0]}"
        )


if __name__ == "__main__":

    conn = create_database()

    load_tables(conn)

    verify_tables(conn)

    conn.close()

    print("\nnifty100.db created successfully")