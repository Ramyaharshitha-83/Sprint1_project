# Sprint 2 Retrospective

## Project Overview

The objective of Sprint 2 was to build a Financial Ratio Engine for the Nifty100 Financial Intelligence Platform. The ratio engine processes company financial data and calculates important financial indicators (KPIs) that help evaluate company performance, profitability, growth, efficiency, and financial health.

The computed ratios are stored in a SQLite database and are later used for company screening, benchmarking, analytics, and dashboard visualizations.

---

## Sprint Goal

To automatically compute 50+ financial KPIs for all Nifty100 companies across all available years and store the results in the `financial_ratios` table.

The sprint also focused on handling special financial cases such as:

* Companies with zero sales or zero assets.
* Companies with negative net worth.
* Debt-free companies.
* Companies belonging to the Financial sector where leverage behaves differently.
* Companies with turnaround or loss-making scenarios.

---

## Work Completed

### 1. Profitability Ratio Engine

Implemented functions to calculate important profitability metrics:

* **Net Profit Margin (NPM)** – Measures how much profit is generated from sales.
* **Operating Profit Margin (OPM)** – Measures operational efficiency.
* **Return on Equity (ROE)** – Measures returns generated for shareholders.
* **Return on Capital Employed (ROCE)** – Evaluates overall capital efficiency.
* **Return on Assets (ROA)** – Measures asset utilization efficiency.

Special handling was added to avoid incorrect calculations when denominator values were zero or negative.

---

### 2. Leverage and Efficiency Ratios

Implemented financial health indicators:

* **Debt-to-Equity Ratio (D/E)** – Measures company leverage.
* **Interest Coverage Ratio (ICR)** – Measures ability to repay interest obligations.
* **Net Debt** – Calculates actual debt burden after adjusting investments.
* **Asset Turnover Ratio** – Measures efficiency in generating sales from assets.

Additional business rules implemented:

* Debt-free companies are labeled as **"Debt Free"**.
* High leverage warnings are generated for non-financial companies.
* Financial companies (banks, NBFCs, insurance) are exempted from high leverage warnings because leverage is normal in those industries.

---

### 3. CAGR Engine

Developed a Compound Annual Growth Rate (CAGR) engine to measure long-term growth in:

* Revenue
* Net Profit (PAT)
* Earnings Per Share (EPS)

The engine supports multiple growth periods and handles several real-world edge cases such as:

* Positive value changing to loss.
* Loss turning into profit (turnaround).
* Negative-to-negative transitions.
* Zero base values.
* Insufficient historical data.

Appropriate flags are generated for each special case.

---

### 4. Cash Flow KPI Engine

Implemented cash flow-based quality metrics:

* **Free Cash Flow (FCF)**
* **CFO Quality Score**
* **CapEx Intensity**
* **FCF Conversion Rate**

Additionally, an 8-pattern Capital Allocation Classifier was developed to classify company cash flow behavior into categories such as:

* Reinvestor
* Shareholder Returns
* Growth Funded by Debt
* Distress Signal
* Cash Accumulator

---

### 5. Database Population

Created an automated ratio engine that:

1. Reads financial data from SQLite tables.
2. Merges Profit & Loss and Balance Sheet information.
3. Computes financial KPIs for every company-year combination.
4. Stores the computed results into the `financial_ratios` table.

A total of **1175 company-year financial ratio records** were generated successfully.

---

### 6. Unit Testing

Comprehensive unit tests were written for all financial formulas.

The tests covered:

* Normal calculation scenarios.
* Zero denominator conditions.
* Negative equity situations.
* Debt-free companies.
* Growth edge cases.
* Capital allocation classifications.

All tests passed successfully, ensuring correctness and reliability of the ratio engine.

---

## Key Design Decisions

* Return `None` whenever financial ratios cannot be calculated safely.
* Label debt-free companies instead of displaying missing values.
* Suppress leverage warnings for financial sector companies.
* Use internally computed ratio values for analytics while retaining source values for display purposes.

---

## Challenges Faced

* Source datasets contained duplicate financial records.
* Some pre-computed source ratios were inconsistent.
* Financial data required extensive validation and exception handling.
* CAGR calculations required handling multiple non-standard scenarios.

---

## Lessons Learned

* Financial analytics systems require significant data validation.
* Edge case handling is essential for reliable KPI computation.
* Unit testing greatly improves confidence in financial calculations.
* Understanding business and accounting concepts is as important as writing code.

---

## Final Outcome

Sprint 2 successfully delivered a fully functional Financial Ratio Engine capable of computing and storing financial KPIs for all available Nifty100 company records.

The generated ratio dataset is now ready for:

* Company screening
* Benchmarking
* Dashboard visualization
* Portfolio analytics
* Advanced financial analysis

The project is prepared for the next development phase.
