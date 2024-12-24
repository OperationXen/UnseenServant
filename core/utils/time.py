from datetime import datetime, timedelta


def a_year_from_now():
    """get a timestamp 1 year hence"""
    now = datetime.now()
    return now + timedelta(days=365)


def a_month_from_now():
    """get a timestamp 1 month hence"""
    now = datetime.now()
    return now + timedelta(days=31)
