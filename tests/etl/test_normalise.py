import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)



def test_year_mar23():
    assert normalize_year("Mar-23") == "2023-03"


def test_year_fy24():
    assert normalize_year("FY24") == "2024-03"


def test_year_dec22():
    assert normalize_year("Dec-22") == "2022-12"


def test_year_full():
    assert normalize_year("March-2023") == "2023-03"


def test_year_integer():
    assert normalize_year("2023") == "2023-03"


def test_year_normalized():
    assert normalize_year("2023-03") == "2023-03"


def test_year_invalid():
    assert normalize_year("xyz") == "PARSE_ERROR"


def test_ticker_upper():
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_strip():
    assert normalize_ticker("  infy ") == "INFY"


def test_ticker_hyphen():
    assert normalize_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO"


def test_ticker_ampersand():
    assert normalize_ticker("M&M") == "M&M"


def test_ticker_none():
    assert normalize_ticker(None) is None