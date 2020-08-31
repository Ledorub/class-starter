import logging
import re
import datetime as dt
from datetime import datetime
from hashlib import md5

import pytz
from bs4 import BeautifulSoup

from project.settings import urls

logger = logging.getLogger()


class ScheduleMeta(type):
    _instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = super().__call__()
        return self._instance


class Schedule(metaclass=ScheduleMeta):
    def __init__(self):
        self._hash = None
        self.last_update = None
        self.schedule = None

    def _get_hash(self, inp):
        if isinstance(inp, str):
            inp = inp.encode()
        return md5(bytes(inp))

    def _set_hash(self, html):
        self.hash = md5(html.encode())

    def _set_last_update(self):
        self.last_update = datetime.now()

    def _fetch(self, session):
        response = session.get(urls['schedule'])
        if response:
            markup = response.text
            return markup

    def get_schedule(self, session):
        markup = self._fetch(session)

        if self._get_hash(markup) != self._hash:
            self.schedule = self._parse(markup)

            self._set_hash(markup)
            self._set_last_update()
        return self.schedule

    def get_current_lesson(self, session):
        self.get_schedule(session)

        now = datetime.utcnow()   # TODO: Check whether works correctly with tz.

        today_schedule = self.schedule[now.date()]
        for start_time, lesson in today_schedule.items():
            lesson_date = datetime.combine(now.date(), start_time)
            end_time = (lesson_date + dt.timedelta(hours=1, minutes=35)).time()

            if start_time <= now.time() < end_time:
                return lesson

    def _parse(self, html):
        soup = BeautifulSoup(html, 'lxml')
        tbody = soup.find('tbody')

        schedule = {}
        lessons = []

        for row in tbody.children:
            try:
                contents = list(row.children)
            except AttributeError:
                continue

            if len(contents) == 2:
                if lessons:
                    schedule[date] = self._parse_day(lessons)
                    lessons = []
                header = row
                date = self._parse_header_date(header)
            else:
                lessons.append(row)
        else:
            if lessons:
                schedule[date] = self._parse_day(lessons)
        return schedule

    def _parse_header_date(self, day_header):
        date = re.search(r'(\d{1,2})-(\d{1,2})-(\d{2,4})', day_header.text)
        date = list(map(int, date.groups()))
        return dt.date(*reversed(date))

    def _parse_day(self, lessons):
        day = {}

        for lesson_data in lessons:
            if lesson_data not in ['\n', '\r', '\t']:
                time, lesson = self._parse_lesson(lesson_data)
                day[time] = lesson
        return day

    def _parse_lesson(self, tr):
        fields = tuple(tr.children)
        lesson = {}

        lesson['name'], lesson['type'] = self._parse_name_type(fields[3])
        time = self._parse_time(fields[1])
        lesson['teacher'] = self._parse_teacher(fields[7])

        sig = self._parse_start_sig(fields[9])
        if sig:
            lesson['start_args'] = self._parse_sig_args(sig)

        return time, lesson

    def _parse_name_type(self, td):
        name = td.find('b').text
        typ = td.find('small').text.split('  ')
        return name, typ[0]

    def _parse_time(self, td):  # TODO: Refactor?
        msc_tz = pytz.timezone('Europe/Moscow')

        lesson_time = re.search(r'\d{1,2}:\d{2}', td.text)
        lesson_time = datetime.strptime(lesson_time.group(), '%H:%M').time()
        lesson_time = datetime.combine(datetime.now().date(), lesson_time)
        lesson_time = msc_tz.localize(lesson_time)
        return lesson_time.astimezone(pytz.UTC).time()

    def _parse_teacher(self, td):
        return td.text

    def _parse_start_sig(self, td):
        tag = td.find('a', onclick=re.compile(r'^[\w_]+\(\d+,\d+\);*'))
        return tag['onclick'] if tag else None

    def _parse_sig_args(self, sig):
        args = re.findall(r'\d+', sig)
        return tuple(map(int, args))
