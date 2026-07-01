from src.analytics.ratios import *

# Net Profit Margin

def test_npm_normal():
    assert net_profit_margin(100, 1000) == 10.0


def test_npm_zero_sales():
    assert net_profit_margin(100, 0) is None


# OPM

def test_opm_normal():
    opm, flag = operating_profit_margin(
        200, 1000, 20
    )

    assert opm == 20.0
    assert flag is False


def test_opm_mismatch():
    opm, flag = operating_profit_margin(
        200, 1000, 10
    )

    assert flag is True


# ROE

def test_roe_normal():
    assert return_on_equity(
        100,
        100,
        400
    ) == 20.0


def test_roe_negative_equity():
    assert return_on_equity(
        100,
        -100,
        -50
    ) is None


# ROCE

def test_roce_normal():
    assert return_on_capital_employed(
        500,
        50,
        1000,
        2000,
        500
    ) == 15.71


# ROA

def test_roa_normal():
    assert return_on_assets(
        100,
        1000
    ) == 10.0


def test_roa_zero_assets():
    assert return_on_assets(
        100,
        0
    ) is None

# Debt to Equity

def test_debt_free():
    ratio, flag = debt_to_equity(
        0,
        100,
        100
    )

    assert ratio == 0
    assert flag is False


def test_high_leverage():
    ratio, flag = debt_to_equity(
        10000,
        100,
        100,
        "Technology"
    )

    assert flag is True


def test_financial_company_leverage():
    ratio, flag = debt_to_equity(
        10000,
        100,
        100,
        "Financials"
    )

    assert flag is False


# Interest Coverage

def test_icr_interest_zero():
    icr, label, flag = interest_coverage_ratio(
        100,
        50,
        0
    )

    assert icr is None
    assert label == "Debt Free"


def test_icr_warning():
    icr, label, flag = interest_coverage_ratio(
        100,
        0,
        100
    )

    assert flag is True


# Net Debt

def test_net_debt():
    assert net_debt(
        1000,
        200
    ) == 800


# Asset Turnover

def test_asset_turnover():
    assert asset_turnover(
        1000,
        500
    ) == 2.0


def test_asset_turnover_zero():
    assert asset_turnover(
        1000,
        0
    ) is None