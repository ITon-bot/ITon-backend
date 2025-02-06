import json

from celery import shared_task
import redis
from django.contrib.contenttypes.models import ContentType
from views.models import View

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@shared_task(name='vacancies.tasks.flush_views_to_db')
def flush_views_to_db():
    """Сбрасываем накопленные просмотры из Redis в БД"""
    from vacancies.models import Vacancy

    views = []
    content_type = ContentType.objects.get_for_model(Vacancy)

    keys = redis_client.keys("vacancy:*:views")

    for key in keys:
        vacancy_id = int(key.split(":")[1])
        redis_views = int(redis_client.get(key) or 0)

        Vacancy.objects.filter(id=vacancy_id).update(views_count=redis_views)

    while redis_client.llen("pending_vacancy_views") > 0:
        view_json = redis_client.lpop("pending_vacancy_views")
        view_data = json.loads(view_json)

        views.append(View(
            user_id=view_data["user_id"],
            content_type=content_type,
            object_id=view_data["vacancy_id"],
            timestamp=view_data["timestamp"]
        ))

    if views:
        View.objects.bulk_create(views)

