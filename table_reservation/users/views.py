from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser
from .serializers import UserRegistrationSerializer
from .utils import send_activation_email

class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя (с отправкой email)"""
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_activation_email(user, self.request)  # Отправляем письмо с активацией
        return Response({"message": "Письмо с активацией отправлено."}, status=status.HTTP_201_CREATED)


class ActivateAccountView(APIView):
    """Активация аккаунта по ссылке из email"""

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.is_email_verified = True
                user.save()
                return Response({"message": "Аккаунт активирован!"}, status=status.HTTP_200_OK)

            return Response({"error": "Неверный токен"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Некорректная ссылка"}, status=status.HTTP_400_BAD_REQUEST)
