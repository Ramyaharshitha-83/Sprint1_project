# Data Quality Manual Review

## Project

Nifty100 Financial Intelligence Platform

## Review Date

Sprint 1 - Day 6

## Objectives

The objective of this review was to manually validate data quality, database loading, year coverage, and overall integrity of the SQLite database generated during the ETL process.

---

## Random Company Validation

Five companies were randomly selected from the database and manually reviewed.

Validation checks performed:

* Company exists in master company table.
* Financial records available in Profit & Loss table.
* Historical year coverage available.
* Data loaded successfully into SQLite database.

Result:

All sampled companies were successfully retrieved from the database and contained historical financial records.

---

## Year Coverage Review

Year coverage was checked for selected companies using the Profit & Loss table.

Observations:

* Historical data is available from approximately Mar 2013 onwards.
* Latest reporting periods include Mar 2024 and TTM (Trailing Twelve Months).
* Most companies contain long-term financial history suitable for trend analysis and KPI computation.

---

## Companies With Less Than 5 Years of Data

Query executed:

```sql
SELECT company_id,
       COUNT(*) as years
FROM profitandloss
GROUP BY company_id
HAVING COUNT(*) < 5;
```

Result:

A small number of companies were identified with limited historical records. These are primarily due to recent listings or limited source data availability.

No critical data completeness issues were identified.

---

## Loader Validation

Database row counts were validated against the generated load_audit.csv file.

Verified Counts:

| Table            | Rows |
| ---------------- | ---: |
| companies        |   92 |
| profitandloss    | 1276 |
| balancesheet     | 1312 |
| cashflow         | 1187 |
| analysis         |   20 |
| documents        | 1585 |
| prosandcons      |   16 |
| sectors          |   92 |
| stock_prices     | 5520 |
| market_cap       |  552 |
| financial_ratios | 1184 |
| peer_groups      |   56 |

Result:

All database table counts matched the load audit report.

---

## Validator Review

Data Quality Validator executed successfully.

Validation Results:

* Total validation failures detected: 4178
* Majority of failures were duplicate company-year combinations.
* Investigation showed that source Excel exports contain duplicate historical record blocks.
* Validation framework correctly identified these duplicate records.

Sample issue:

* ADANIPORTS – Mar 2013
* ADANIPORTS – Mar 2014
* ADANIPORTS – Mar 2015

Issue Type:

Duplicate company-year records.

Severity:

CRITICAL

Result:

Validator functioning as expected.

---

## Conclusion

The ETL pipeline, validation framework, SQLite database creation, and dataset loading process were successfully verified.

All required datasets were loaded into the database, audit reports were generated, and manual validation confirmed data availability and integrity.

The dataset is ready for analytical processing, KPI computation, screening, benchmarking, and reporting activities in subsequent project phases.
