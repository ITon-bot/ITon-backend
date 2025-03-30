import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

celery_app = Celery('core')

celery_app.config_from_object('django.conf:settings', namespace='CELERY')

celery_app.autodiscover_tasks()


@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


celery_app.conf.beat_schedule = {
    'flush-views-every-minute': {
        'task': 'vacancies.tasks.flush_views_to_db',
        'schedule': crontab(minute='*/1'),
    },
}
