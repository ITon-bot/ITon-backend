import json
from os import environ

import requests

def send_telegram_notification(chat_id: str, text: str, reply_markup: dict = None):
    token = environ.get('BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, data=data)


def perform_update_and_notify(view, request, update_method, field_name, notification_func):
    """
    Выполняет обновление объекта с помощью update_method и проверяет изменение указанного поля.
    Если значение поля (field_name) изменилось, вызывает notification_func.

    :param view: экземпляр view (self) с методом get_object()
    :param request: HTTP-запрос
    :param update_method: функция (например, lambda), которая вызывает super().update(...) или partial_update(...)
    :param field_name: имя поля, за которым ведется наблюдение (например, 'status' или 'approval_status')
    :param notification_func: функция уведомления с сигнатурой notification_func(instance, extra_message)
    :return: результат update_method (HTTP Response)
    """
    instance = view.get_object()
    old_value = getattr(instance, field_name)

    response = update_method()

    instance.refresh_from_db()
    new_value = getattr(instance, field_name)

    extra_message = request.data.get('custom_message')
    if old_value != new_value:
        notification_func(instance, extra_message)

    return response
