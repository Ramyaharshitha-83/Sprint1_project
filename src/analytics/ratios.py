"""
Profitability Ratio Engine
Sprint 2 - Day 08
"""


def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = Net Profit / Sales * 100
    """

    if sales is None or sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)


def operating_profit_margin(operating_profit,
                             sales,
                             source_opm=None):
    """
    Operating Profit Margin.
    Returns computed OPM and mismatch flag.
    """

    if sales is None or sales == 0:
        return None, False

    computed_opm = round(
        (operating_profit / sales) * 100,
        2
    )

    mismatch = False

    if source_opm is not None:
        if abs(computed_opm - source_opm) > 1:
            mismatch = True

    return computed_opm, mismatch


def return_on_equity(net_profit,
                     equity_capital,
                     reserves):
    """
    ROE = Net Profit / (Equity + Reserves) *100
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(
        (net_profit / equity) * 100,
        2
    )


def return_on_capital_employed(
        operating_profit,
        interest,
        equity_capital,
        reserves,
        borrowings):
    """
    ROCE = EBIT / Capital Employed
    EBIT = Operating Profit + Interest
    """

    capital_employed = (
        equity_capital +
        reserves +
        borrowings
    )

    if capital_employed <= 0:
        return None

    ebit = operating_profit + interest

    return round(
        (ebit / capital_employed) * 100,
        2
    )


def return_on_assets(net_profit,
                     total_assets):
    """
    ROA = Net Profit / Total Assets
    """

    if total_assets is None or total_assets == 0:
        return None

    return round(
        (net_profit / total_assets) * 100,
        2
    )

def debt_to_equity(
        borrowings,
        equity_capital,
        reserves,
        sector=None):
    """
    Debt to Equity Ratio
    """

    if borrowings == 0:
        return 0, False

    equity = equity_capital + reserves

    if equity <= 0:
        return None, False

    ratio = round(
        borrowings / equity,
        2
    )

    high_leverage_flag = False

    if ratio > 5 and sector != "Financials":
        high_leverage_flag = True

    return ratio, high_leverage_flag


def interest_coverage_ratio(
        operating_profit,
        other_income,
        interest):
    """
    Interest Coverage Ratio
    """

    if interest == 0:
        return None, "Debt Free", False

    icr = round(
        (operating_profit + other_income)
        / interest,
        2
    )

    warning_flag = False

    if icr < 1.5:
        warning_flag = True

    return icr, None, warning_flag


def net_debt(
        borrowings,
        investments):
    """
    Net Debt
    """

    return borrowings - investments


def asset_turnover(
        sales,
        total_assets):
    """
    Asset Turnover
    """

    if total_assets == 0:
        return None

    return round(
        sales / total_assets,
        2
    )