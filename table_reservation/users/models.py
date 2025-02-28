from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя (обычного и админа)"""

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт пользователя (обычного или администратора)"""
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)

        extra_fields.setdefault("is_active", False)  # По умолчанию пользователи неактивны
        extra_fields.setdefault("is_email_verified", False)  # Email нужно подтверждать

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт суперпользователя (без дублирования кода)"""
        extra_fields.update({"is_staff": True, "is_superuser": True, "is_active": True, "is_email_verified": True})
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с аутентификацией по email"""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)  # Блокируем вход без подтверждения
    is_staff = models.BooleanField(default=False)  # Админские права
    is_superuser = models.BooleanField(default=False)  # Полные права
    is_email_verified = models.BooleanField(default=False)  # Подтверждение email

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
