from src.analytics.cashflow_kpis import *


def test_free_cash_flow():
    assert free_cash_flow(
        1000, -400
    ) == 600


def test_cfo_quality_high():
    assert cfo_quality_score(
        1200, 1000
    ) == "High Quality"


def test_cfo_quality_moderate():
    assert cfo_quality_score(
        700, 1000
    ) == "Moderate"


def test_cfo_quality_risk():
    assert cfo_quality_score(
        300, 1000
    ) == "Accrual Risk"


def test_cfo_quality_zero_pat():
    assert cfo_quality_score(
        1000, 0
    ) is None


def test_capex_asset_light():
    _, label = capex_intensity(
        -20, 1000
    )

    assert label == "Asset Light"


def test_capex_capital_intensive():
    _, label = capex_intensity(
        -200, 1000
    )

    assert label == "Capital Intensive"


def test_fcf_conversion():
    assert fcf_conversion_rate(
        500, 1000
    ) == 50.0


def test_reinvestor():
    assert classify_capital_allocation(
        100, -50, -20
    ) == "Reinvestor"


def test_distress_signal():
    assert classify_capital_allocation(
        -100, 50, 20
    ) == "Distress Signal"