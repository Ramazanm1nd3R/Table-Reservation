from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """Настройка отображения модели пользователя в Django Admin"""
    
    model = CustomUser
    list_display = ("email", "is_active", "is_staff", "is_superuser")  # Какие поля отображать
    list_filter = ("is_active", "is_staff", "is_superuser")  # Фильтры
    ordering = ("email",)  # Сортировка по email
    search_fields = ("email",)  # Поиск

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Разрешения", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Даты", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
