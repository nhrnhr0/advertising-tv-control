from __future__ import absolute_import, unicode_literals
from server.settings.secrects import DJANGO_SETTINGS_MODULE, BROKER_USER, BROKER_PASSWORD
import os
from celery.schedules import crontab
from celery import Celery
#BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)
# save Celery task results in Django's database
CELERY_RESULT_BACKEND = "django-db"

app = Celery('server', broker='amqp://'+BROKER_USER + ':' + BROKER_PASSWORD + '@localhost//')

app.config_from_object('django.conf:settings', namespace='CELERY')
#from celery.schedules import crontab

app.autodiscover_tasks()
#app.conf.broker_url = BASE_REDIS_URL
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

from .tasks import monitor_pi_devices


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    
    
    sender.add_periodic_task(10.0, monitor_pi_devices.s(), name='monitor_pi_devices') # half an hour

    # # Calls test('world') every 30 seconds
    # sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     test.s('Happy Mondays!'),
    # )
    pass
# @app.task
# def test(arg):
#     print(arg)

# @app.task
# def add(x, y):
#     z = x + y
#     print(z)