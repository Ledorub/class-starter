from celery import Celery

import project.settings
from project.settings import TIME_ZONE

app = Celery()

app.conf.timezone = TIME_ZONE
app.config_from_object(project.settings, namespace='CELERY')

app.autodiscover_tasks(['project'])
