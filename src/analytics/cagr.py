"""
CAGR Engine
Sprint 2 - Day 10
"""


def calculate_cagr(start_value, end_value, years):
    """
    CAGR Formula:
    ((end/start)^(1/n)-1)*100

    Returns:
    (cagr_value, flag)
    """

    # Insufficient years
    if years <= 0:
        return None, "INSUFFICIENT"

    # Zero base
    if start_value == 0:
        return None, "ZERO_BASE"

    # Positive -> Negative
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # Negative -> Positive
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    # Negative -> Negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # Normal case
    cagr = (
        ((end_value / start_value) ** (1 / years))
        - 1
    ) * 100

    return round(cagr, 2), None