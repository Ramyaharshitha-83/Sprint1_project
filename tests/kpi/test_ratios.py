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