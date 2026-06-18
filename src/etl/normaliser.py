import re
from datetime import datetime


def normalize_ticker(ticker: str) -> str:
    """
    Normalize NSE ticker symbol.
    """
    if ticker is None:
        return None

    ticker = str(ticker).strip().upper()

    if len(ticker) < 2 or len(ticker) > 12:
        return None

    return ticker


def normalize_year(year_value: str) -> str:
    """
    Convert year formats to YYYY-MM.
    """

    if year_value is None:
        return "PARSE_ERROR"

    value = str(year_value).strip()

    month_map = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12"
    }

    if re.match(r"^\d{4}-\d{2}$", value):
        return value

    if re.match(r"^\d{4}$", value):
        return f"{value}-03"

    value = value.replace("FY", "").strip()

    if re.match(r"^\d{2}$", value):
        year = 2000 + int(value)
        return f"{year}-03"

    patterns = [
        "%b-%y",
        "%b %y",
        "%B-%Y"
    ]

    for pattern in patterns:
        try:
            dt = datetime.strptime(value, pattern)
            return dt.strftime("%Y-%m")
        except ValueError:
            pass

    return "PARSE_ERROR"