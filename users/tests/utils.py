import json
import hmac
import hashlib
from urllib.parse import quote, unquote


def create_valid_token(secret_key, user_data):
    """
    Создаёт валидный токен для тестов.
    :param secret_key: Секретный ключ (BOT_TOKEN).
    :param user_data: Данные пользователя (dict).
    :return: Строка токена вида: "hash=abc123&user=..."
    """
    user_json = json.dumps(user_data)
    user_encoded = quote(user_json)

    init_data = f"user={user_encoded}"

    init_data_sorted = sorted(
        [chunk.split("=") for chunk in unquote(init_data).split("&")],
        key=lambda x: x[0]
    )
    init_data_sorted = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data_sorted])

    secret = hmac.new("WebAppData".encode(), secret_key.encode(), hashlib.sha256).digest()
    hash_str = hmac.new(secret, init_data_sorted.encode(), hashlib.sha256).hexdigest()

    return f"hash={hash_str}&{init_data}"
