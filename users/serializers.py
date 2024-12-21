from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id', 'first_name', 'last_name', 'photo_url']

    def validate_tg_id(self, value):
        if User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Пользователь с таким id уже существует.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
