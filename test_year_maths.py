# tests/test_year_math.py

from main import parse_year, advance_year, calendar_distance

def test_parse_year():
    assert parse_year("380 BC") == -380
    assert parse_year("379AD") == 379
    assert parse_year(-1) == -1

def test_advance_year():
    assert advance_year(-380) == -379
    assert advance_year(-1) == 1      # no year 0
    assert advance_year(1) == 2

def test_calendar_distance():
    assert calendar_distance(-380, -379) == 1
    assert calendar_distance(-10, -1) == 9
    assert calendar_distance(-1, 1) == 1       # skips year 0
