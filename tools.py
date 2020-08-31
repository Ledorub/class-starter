from datetime import datetime
import pytz

from project.secret import bonch_login, bonch_pass
from project.settings import TIME_ZONE, urls


# Getting cookies
def get_cookies(session):
    response = session.get(urls['login'])
    return response


# Authenticating
def auth(session):
    response = session.post(urls['auth'], auth=(bonch_login, bonch_pass))
    return response


def get_next_midnight():
    tz = pytz.timezone(TIME_ZONE)
    today = datetime.now().date()
    midnight = datetime(today.year, today.month, today.day + 1)
    local_midnight = tz.localize(midnight)
    return local_midnight
