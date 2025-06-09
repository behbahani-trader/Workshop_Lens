from datetime import datetime
import jdatetime

def to_jalali(dt):
    """Convert Gregorian datetime to Jalali datetime"""
    if isinstance(dt, datetime):
        return jdatetime.datetime.fromgregorian(datetime=dt)
    return None

def format_jalali(dt, format='%Y/%m/%d'):
    """Format Jalali datetime to string"""
    if isinstance(dt, datetime):
        jdt = to_jalali(dt)
        return jdt.strftime(format)
    return None

def parse_jalali(date_str, format='%Y/%m/%d'):
    """Parse Jalali date string to Gregorian datetime"""
    try:
        jdt = jdatetime.datetime.strptime(date_str, format)
        return jdt.togregorian()
    except:
        return None 