from src.analytics.cagr import calculate_cagr


def test_normal_cagr():
    cagr, flag = calculate_cagr(
        100, 200, 5
    )

    assert round(cagr, 2) == 14.87
    assert flag is None


def test_turnaround():
    cagr, flag = calculate_cagr(
        -100, 200, 5
    )

    assert cagr is None
    assert flag == "TURNAROUND"


def test_decline_to_loss():
    cagr, flag = calculate_cagr(
        100, -200, 5
    )

    assert cagr is None
    assert flag == "DECLINE_TO_LOSS"


def test_both_negative():
    cagr, flag = calculate_cagr(
        -100, -200, 5
    )

    assert cagr is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():
    cagr, flag = calculate_cagr(
        0, 100, 5
    )

    assert cagr is None
    assert flag == "ZERO_BASE"


def test_insufficient_years():
    cagr, flag = calculate_cagr(
        100, 200, 0
    )

    assert cagr is None
    assert flag == "INSUFFICIENT"


def test_positive_growth():
    cagr, flag = calculate_cagr(
        100, 300, 10
    )

    assert round(cagr, 2) == 11.61


def test_flat_growth():
    cagr, flag = calculate_cagr(
        100, 100, 5
    )

    assert cagr == 0.0


def test_small_growth():
    cagr, flag = calculate_cagr(
        100, 110, 5
    )

    assert round(cagr, 2) == 1.92


def test_large_growth():
    cagr, flag = calculate_cagr(
        100, 1000, 10
    )

    assert round(cagr, 2) == 25.89