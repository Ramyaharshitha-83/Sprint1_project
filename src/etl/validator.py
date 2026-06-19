"""
Data Quality Validator
Sprint 1 - Day 3
"""

import pandas as pd
import re

from src.etl.loader import load_core_dataset

# Store all validation failures
failures = []


# =========================
# Load Datasets
# =========================

companies = load_core_dataset("companies.xlsx")
profitandloss = load_core_dataset("profitandloss.xlsx")
balancesheet = load_core_dataset("balancesheet.xlsx")
cashflow = load_core_dataset("cashflow.xlsx")


# =========================
# DQ-01 Company PK Uniqueness
# =========================

def check_company_uniqueness():
    duplicates = companies[
        companies["id"].duplicated()
    ]

    for _, row in duplicates.iterrows():
        failures.append({
            "company_id": row["id"],
            "year": "",
            "field": "id",
            "issue": "Duplicate company id",
            "severity": "CRITICAL"
        })


# =========================
# DQ-02 Company-Year Uniqueness
# =========================

def check_duplicate_company_year(df, table_name):

    duplicates = df[
        df.duplicated(
            subset=["company_id", "year"]
        )
    ]

    for _, row in duplicates.iterrows():
        failures.append({
            "company_id": row["company_id"],
            "year": row["year"],
            "field": table_name,
            "issue": "Duplicate company-year",
            "severity": "CRITICAL"
        })


# =========================
# DQ-03 Foreign Key Integrity
# =========================

def check_foreign_key(df, table_name):

    valid_companies = set(
        companies["id"]
    )

    invalid_rows = df[
        ~df["company_id"].isin(
            valid_companies
        )
    ]

    for _, row in invalid_rows.iterrows():
        failures.append({
            "company_id": row["company_id"],
            "year": row["year"],
            "field": table_name,
            "issue": "Foreign key missing",
            "severity": "CRITICAL"
        })


# =========================
# DQ-07 Year Format Validation
# =========================

def check_year_format(df, table_name):

    pattern = r"^\d{4}-\d{2}$"

    for _, row in df.iterrows():

        year_value = str(
            row["year"]
        )

        if not re.match(
            pattern,
            year_value
        ):
            failures.append({
                "company_id": row["company_id"],
                "year": year_value,
                "field": "year",
                "issue": f"Invalid year format in {table_name}",
                "severity": "CRITICAL"
            })


# =========================
# Run All Checks
# =========================

check_company_uniqueness()

check_duplicate_company_year(
    profitandloss,
    "profitandloss"
)

check_duplicate_company_year(
    balancesheet,
    "balancesheet"
)

check_duplicate_company_year(
    cashflow,
    "cashflow"
)

check_foreign_key(
    profitandloss,
    "profitandloss"
)

check_foreign_key(
    balancesheet,
    "balancesheet"
)

check_foreign_key(
    cashflow,
    "cashflow"
)

check_year_format(
    profitandloss,
    "profitandloss"
)

check_year_format(
    balancesheet,
    "balancesheet"
)

check_year_format(
    cashflow,
    "cashflow"
)


# =========================
# Save Results
# =========================

validation_df = pd.DataFrame(failures)

validation_df.to_csv(
    "validation_failures.csv",
    index=False
)

print("=" * 50)
print("DATA QUALITY VALIDATION REPORT")
print("=" * 50)
print(f"Total Failures Found: {len(validation_df)}")

if len(validation_df) > 0:
    print("\nSample Failures:")
    print(validation_df.head())
else:
    print("\nNo validation failures found.")

print("\nvalidation_failures.csv generated successfully.")

duplicates = profitandloss[
    profitandloss.duplicated(
        subset=["company_id", "year"],
        keep=False
    )
]

print(duplicates.head(20))