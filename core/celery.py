from os import environ

from celery import Celery
from celery.schedules import crontab

APP_NAME = 'core'

# Устанавливаем переменную окружения для настроек Django
environ.setdefault('DJANGO_SETTINGS_MODULE', APP_NAME + '.settings')

# Инициализируем Celery с именем проекта
celery_app = Celery(APP_NAME)
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

# Настраиваем периодическую задачу
celery_app.conf.beat_schedule = {
    'flush-views-every-5-minutes': {
        'task': 'vacancies.tasks.flush_views_to_db',
        'schedule': crontab(minute='*/1'),
    },
    'update-views-count-every-minute': {
        'task': 'vacancies.tasks.update_views_count',
        'schedule': crontab(minute='*/1'),
    },
}
