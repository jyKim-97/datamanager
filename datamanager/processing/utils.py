# import datetime, timedelta
from datetime import datetime, timedelta


def strftime_hms(t0: datetime):
    s1 = t0.strftime("%H:%M:%S")
    s2 = "_%03d"%(t0.microsecond // 1000)
    return s1 + s2


def timedelta_to_hms(dt_delta: timedelta):
    total_seconds = dt_delta.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    ms = dt_delta.microseconds // 1000
    # milliseconds = int((total_seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}_{ms:03}"