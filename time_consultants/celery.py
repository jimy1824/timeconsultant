from __future__ import absolute_import, unicode_literals

import os

from django.conf import settings
from celery.schedules import crontab
from celery import Celery
from . import celeryconfig

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time_consultants.settings')

app = Celery('time_consultants',
             broker=celeryconfig.broker_url,
             backend=celeryconfig.result_backend,
             )
app.config_from_object("time_consultants.celeryconfig")
app.autodiscover_tasks()

app.conf.beat_schedule = {
   'currency_value': {
        'task': 'common.tasks.currency_base_values',
        'schedule': crontab(minute='*/30')
    },
    'currency': {
        'task': 'common.tasks.currency_converter',
        'schedule': crontab(minute='*/30')
    },

}

