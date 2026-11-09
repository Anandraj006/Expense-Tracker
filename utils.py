from datetime import date


def month_range(month, year):
    """Returns (first day, first day of next month) as 'YYYY-MM-DD'.
    Use as: date >= start AND date < end (keeps the date index usable)."""
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start.isoformat(), end.isoformat()


def year_range(year):
    return date(year, 1, 1).isoformat(), date(year + 1, 1, 1).isoformat()