from urllib.parse import unquote
import json
import hmac
import hashlib
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from os import environ
from users.models import User


def telegram_auth(view_func):
    view_func.telegram_auth = True
    return csrf_exempt(view_func)


class TelegramWebAppAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request: HttpRequest):
        token = request.headers.get('Authorization', '').replace('tma ', '').strip()
        validated, user_dict = self.validate(token)

        if not validated:
            return HttpResponse(status=403)

        request.telegram_user, _ = User.login(user_dict)

        if request.telegram_user.is_blocked:
            return HttpResponse(status=403)

        return None

    @classmethod
    def validate(cls, token: str) -> (bool, dict):
        """
        Проверяет токен Telegram и валидирует его
        :param token: Токен с данными
        :return: True/False и данные пользователя
        """
        if not token:
            print("No token provided")
            return False, None

        try:
            parsed_token = cls.parse_token(token)

            control_hash = parsed_token.pop('hash', None)
            if not control_hash:
                print("No control hash in token")
                return False, None

            init_data = '&'.join([f"{key}={value}" for key, value in parsed_token.items()])

            secret_key = environ.get('BOT_TOKEN')
            if not secret_key:
                raise ValueError("BOT_TOKEN environment variable is not set")

            is_valid = cls.check_validate_init_data(control_hash, init_data, secret_key)
            if not is_valid:
                print("Hashes do not match")
                return False, None

            user_dict = json.loads(parsed_token.get('user', '{}'))
            return is_valid, user_dict

        except Exception as e:
            print(f"Error validating token: {e}")
            return False, None

    @staticmethod
    def parse_token(token: str) -> dict:
        """Парсит токен Telegram в словарь"""
        parsed_token = {}
        for param in unquote(token).split('&'):
            key_value = param.split('=')
            if len(key_value) == 2:
                parsed_token[key_value[0]] = key_value[1]
            else:
                raise ValueError(f"Invalid token parameter: {param}")
        return parsed_token

    @staticmethod
    def check_validate_init_data(hash_str, init_data, token, c_str="WebAppData"):
        """
        Проверяет данные и хэш
        :param hash_str: Хэш, переданный в токене
        :param init_data: Строка данных
        :param token: Секретный ключ Telegram
        :param c_str: Строка константы, используемая для создания хэша
        :return: True, если хэш совпадает
        """
        init_data = sorted(
            [chunk.split("=") for chunk in unquote(init_data).split("&") if not chunk.startswith("hash=")],
            key=lambda x: x[0]
        )
        init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

        secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()
        data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

        return data_check.hexdigest() == hash_str
