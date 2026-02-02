import re
import time

def is_valid_url(url):
    regex = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def format_time(ts_string):
    try:
        dt = time.strptime(ts_string.split('.')[0], "%Y-%m-%d %H:%M:%S")
        return time.strftime("%H:%M:%S", dt)
    except:
        return ts_string
