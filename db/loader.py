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

    audit_rows = []

    datasets = [
        ("companies", load_core_dataset("companies.xlsx")),
        ("profitandloss", load_core_dataset("profitandloss.xlsx")),
        ("balancesheet", load_core_dataset("balancesheet.xlsx")),
        ("cashflow", load_core_dataset("cashflow.xlsx")),
        ("analysis", load_core_dataset("analysis.xlsx")),
        ("documents", load_core_dataset("documents.xlsx")),
        ("prosandcons", load_core_dataset("prosandcons.xlsx"))
    ]

    supporting = {
        "sectors": "sectors.xlsx",
        "stock_prices": "stock_prices.xlsx",
        "market_cap": "market_cap.xlsx",
        "financial_ratios": "financial_ratios.xlsx",
        "peer_groups": "peer_groups.xlsx"
    }

    for table, file in supporting.items():

        df = pd.read_excel(
            f"data/supporting/{file}"
        )

        datasets.append((table, df))

    for table_name, df in datasets:

        rows_before = len(df)

        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )

        audit_rows.append({
            "table_name": table_name,
            "rows_loaded": rows_before
        })

        print(
            f"Loaded {table_name}: "
            f"{rows_before} rows"
        )

    audit_df = pd.DataFrame(
        audit_rows
    )

    audit_df.to_csv(
        "load_audit.csv",
        index=False
    )

    print(
        "\nload_audit.csv generated"
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