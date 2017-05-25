from datetime import tzinfo, timedelta, datetime


ZERO = timedelta(0)

class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO

utc = UTC()

def datetime_now_utc():
	return datetime.now(utc)

def is_past_due(date):
    delta = date - datetime_now_utc()
    return delta.days < 0

def is_within_threshold(date):
    delta = date - datetime_now_utc()
    return (delta.days >= 0 and delta.days <= 10)

def is_coming_due(date):
    delta = date - datetime_now_utc()
    return (delta.days > 10)

def totimestamp(date):
    return int((date - datetime(1970, 1, 1, tzinfo=utc)).total_seconds())

def format_to_2_digits(num):
    return str(num) if num >= 10 else '0' + str(num)

def can_read_inspection(user):
    try:
        return user.userprofile.role.can_read_inspection
    except:
        return False

def can_write_inspection(user):
    try:
        return user.userprofile.role.can_write_inspection
    except:
        return False

def can_read_gantt(user):
    try:
        return user.userprofile.role.can_read_gantt
    except:
        return False

def can_write_gantt(user):
    try:
        return user.userprofile.role.can_write_gantt
    except:
        return False

def ndigits(value, digits = 1):
    s = str(value)
    while len(s) < digits:
        s = '0' + s
    return s
