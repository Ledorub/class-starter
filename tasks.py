from time import sleep

from celery import shared_task
import pytz

from project.tools import auth, get_cookies
from project.schedule import Schedule
from project.sessions import get_retry_session
from project.settings import urls
from project.tools import get_next_midnight


@shared_task
def start_lesson():
    url = urls['start_class']
    session = get_retry_session()

    if get_cookies(session).ok and auth(session).ok:
        for i in range(15):
            schedule = Schedule()
            lesson = schedule.get_current_lesson(session)

            args = lesson.get('start_args')

            if args:
                data = {'open': 1, 'rasp': args[0], 'week': args[1]}

                print(url, data)
                r = session.post(url, data=data)
                if r.ok:
                    return r.text
            sleep(60)


@shared_task
def every_midnight(func):
    if isinstance(func, str):
        func_name = func.split('.')[-1]

        # Won't find function if it's not global.
        func = globals().get(func_name)
    else:
        func_name = func.__name__.split('.')[-1]

    def wrapper():
        func()

        eta = get_next_midnight()
        every_midnight.apply_async((func_name,), eta=eta.astimezone(pytz.UTC))
    return wrapper
