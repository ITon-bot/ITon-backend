import hmac
import hashlib
import json
from os import environ
from urllib.parse import unquote
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from users.models import User


class TelegramTokenAuthentication(BaseAuthentication):
    keyword = 'tma'

    def authenticate(self, request):
        """
        1) Достаем заголовок Authorization,
        2) Проверяем префикс "tma ",
        3) Валидируем токен,
        4) Возвращаем (user, None) если всё ок
        """
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith(f'{self.keyword} '):
            return None

        token = auth_header.replace(f'{self.keyword} ', '').strip()
        validated, user_dict, error = self.validate_telegram_token(token)
        if not validated:
            raise AuthenticationFailed(error)

        user, _ = User.login(user_dict)
        if user.is_blocked:
            raise AuthenticationFailed("User is blocked")

        return (user, None)

    @classmethod
    def validate_telegram_token(cls, token: str):
        """
        Логика, аналогичная вашей старой validate().
        """
        if not token:
            return False, None, "No token provided"

        try:
            parsed_token = cls.parse_token(token)

            control_hash = parsed_token.pop('hash', None)
            if not control_hash:
                return False, None, "No control hash in token"

            init_data = '&'.join([f"{k}={v}" for k, v in parsed_token.items()])

            secret_key = environ.get('BOT_TOKEN')
            if not secret_key:
                return False, None, "BOT_TOKEN environment variable is not set"

            is_valid = cls.check_validate_init_data(control_hash, init_data, secret_key)
            if not is_valid:
                return False, None, "Hashes do not match"

            user_dict = json.loads(parsed_token.get('user', '{}'))
            return True, user_dict, None

        except Exception as e:
            return False, None, f"Error validating token: {e}"

    @staticmethod
    def parse_token(token: str) -> dict:
        parsed_token = {}
        for param in unquote(token).split('&'):
            key_value = param.split('=')
            if len(key_value) == 2:
                parsed_token[key_value[0]] = key_value[1]
            else:
                raise ValueError(f"Invalid token parameter: {param}")
        return parsed_token

    @staticmethod
    def check_validate_init_data(hash_str, init_data, bot_token, c_str="WebAppData"):
        init_data = sorted(
            [chunk.split("=") for chunk in unquote(init_data).split("&") if not chunk.startswith("hash=")],
            key=lambda x: x[0]
        )
        init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

        secret_key = hmac.new(c_str.encode(), bot_token.encode(), hashlib.sha256).digest()
        data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

        return data_check.hexdigest() == hash_str
