from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['tg_id', 'first_name', 'last_name', 'photo']

    def validate_tg_id(self, value):
        if User.objects.filter(tg_id=value).exists():
            raise serializers.ValidationError("Пользователь с таким tg_id уже существует.")
        return value
