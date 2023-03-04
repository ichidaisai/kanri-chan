import datetime


def is_datetime(string):
    try:
        datetime.datetime.strptime(string, "%Y/%m/%d %H:%M")
    except Exception:
        return False
    return True
