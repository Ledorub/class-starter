import datetime as dt
import logging
import subprocess
import sys

import pytz

from project.celery_app import app
from project.schedule import Schedule
from project.sessions import get_retry_session
from project.settings import TIME_ZONE
from project.tasks import start_lesson, every_midnight
from project.tools import auth, get_cookies

logger = logging.getLogger(__name__)

tz = pytz.timezone(TIME_ZONE)
session = get_retry_session()

if not get_cookies(session).ok:
    sys.exit(1)

if not auth(session).ok:
    sys.exit(1)


def enqueue_lessons():
    s = Schedule()
    schedule = s.get_schedule(session)
    print(schedule)

    for day in schedule:
        for time in schedule[day].keys():
            date = dt.datetime.combine(day, time)
            if dt.datetime.utcnow() < date + dt.timedelta(hours=1, minutes=30):
                start_lesson.apply_async(eta=date)


def celery_purge():
    app.control.purge()


def run_workers():
    subprocess.run([
        'celery', 'worker', '-A', 'project.celery_app',
        '--pool', 'solo', '--loglevel', 'debug'
    ])


if __name__ == '__main__':
    celery_purge()
    every_midnight(enqueue_lessons)()  # This doesn't work and I don't want to fix it.
    run_workers()
