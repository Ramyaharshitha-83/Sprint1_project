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