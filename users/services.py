import hashlib
import hmac


def validate_telegram_data(data: dict, bot_token: str) -> bool:
    """
    Проверяет подпись данных от Telegram.

    :param data: Данные, полученные от TMA.
    :param bot_token: Токен вашего бота Telegram.
    :return: True, если подпись корректна, иначе False.
    """
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    check_hash = data.pop('hash', None)
    if not check_hash:
        return False

    sorted_data = "\n".join([f"{k}={v}" for k, v in sorted(data.items())])
    calculated_hash = hmac.new(secret_key, sorted_data.encode(), hashlib.sha256).hexdigest()

    return check_hash == calculated_hash
