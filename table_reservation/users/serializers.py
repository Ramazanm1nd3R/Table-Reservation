from rest_framework import serializers
from .models import CustomUser
from .utils import Util
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя с email-верификацией"""
    
    class Meta:
        model = CustomUser
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Создаёт пользователя и отправляет письмо для подтверждения email"""
        user = CustomUser.objects.create_user(**validated_data)

        # Генерируем ссылку для подтверждения email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = f"http://127.0.0.1:8000/api/auth/activate/{uid}/{token}/"

        # Отправляем email
        email_data = {
            "email_subject": "Подтверждение регистрации",
            "email_body": f"Привет, {user.email}!\nПодтвердите ваш аккаунт: {activation_link}",
            "to_email": [user.email],
        }
        Util.send_email(email_data)

        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Кастомный сериализатор для JWT, добавляет user-info в ответ"""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "is_email_verified": self.user.is_email_verified,
        }
        return data
