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
