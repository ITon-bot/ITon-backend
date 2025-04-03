import hashlib
import hmac
from django.test import TestCase
from users.services import validate_telegram_data


class ValidateTelegramDataTest(TestCase):

    def setUp(self):
        self.bot_token = "test_bot_token"
        self.secret_key = hashlib.sha256(self.bot_token.encode()).digest()
        self.valid_data = {
            "id": "123456",
            "username": "testuser",
            "auth_date": "1700000000",
        }
        self.invalid_data = self.valid_data.copy()

        sorted_data = "\n".join([f"{k}={v}" for k, v in sorted(self.valid_data.items())])
        check_hash = hmac.new(self.secret_key, sorted_data.encode(), hashlib.sha256).hexdigest()
        self.valid_data["hash"] = check_hash

    def test_valid_signature(self):
        self.assertTrue(validate_telegram_data(self.valid_data, self.bot_token))

    def test_missing_hash(self):
        data = self.valid_data.copy()
        del data["hash"]
        self.assertFalse(validate_telegram_data(data, self.bot_token))

    def test_invalid_signature(self):
        self.invalid_data["hash"] = "invalid_hash"
        self.assertFalse(validate_telegram_data(self.invalid_data, self.bot_token))
