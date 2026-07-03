
def free_cash_flow(
        operating_activity,
        investing_activity):
    """
    FCF = CFO + CFI
    """

    return operating_activity + investing_activity


def cfo_quality_score(
        avg_cfo,
        avg_pat):
    

    if avg_pat == 0:
        return None

    ratio = avg_cfo / avg_pat

    if ratio > 1:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_intensity(
        investing_activity,
        sales):
    

    if sales == 0:
        return None, None

    intensity = round(
        abs(investing_activity) / sales * 100,
        2
    )

    if intensity < 3:
        label = "Asset Light"

    elif intensity <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return intensity, label


def fcf_conversion_rate(
        free_cash_flow_value,
        operating_profit):
    

    if operating_profit == 0:
        return None

    return round(
        free_cash_flow_value /
        operating_profit * 100,
        2
    )


def classify_capital_allocation(
        cfo,
        cfi,
        cff,
        cfo_pat_ratio=None):
   

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):
        if cfo_pat_ratio and cfo_pat_ratio > 1:
            return "Shareholder Returns"
        return "Reinvestor"

    if signs == ("+", "+", "-"):
        return "Liquidating Assets"

    if signs == ("-", "+", "+"):
        return "Distress Signal"

    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if signs == ("+", "+", "+"):
        return "Cash Accumulator"

    if signs == ("-", "-", "-"):
        return "Pre-Revenue"

    if signs == ("+", "-", "+"):
        return "Mixed"

    return "Unclassified"