from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя"""

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя"""
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Хеширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт суперпользователя"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с аутентификацией по email"""
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)  # Позволяет блокировать пользователя
    is_staff = models.BooleanField(default=False)  # Доступ в админ-панель

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Логин теперь через email
    REQUIRED_FIELDS = []  # Django требует, чтобы это был список, но у нас ничего не обязательно

    def __str__(self):
        return self.email
