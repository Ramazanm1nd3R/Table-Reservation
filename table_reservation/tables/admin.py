from django.contrib import admin
from .models import Table, Reservation

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """Управление столиками в админке"""
    list_display = ("number", "seats", "table_type", "is_available")  # Отображаемые поля
    list_filter = ("table_type", "is_available")  # Фильтрация по типу и доступности
    search_fields = ("number",)  # Поиск по номеру столика
    ordering = ("number",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Управление бронированиями в админке"""
    list_display = ("user", "table", "reservation_time", "duration", "status", "created_at")  # Какие поля показывать
    list_filter = ("status", "reservation_time")  # Фильтры
    search_fields = ("user__email", "table__number")  # Поиск по email пользователя и номеру столика
    ordering = ("-reservation_time",)  # Новые бронирования в начале

    actions = ["mark_as_confirmed", "mark_as_cancelled"]  # Добавляем кастомные действия

    def mark_as_confirmed(self, request, queryset):
        """Отметить бронирование как подтверждённое"""
        queryset.update(status="confirmed")
        self.message_user(request, "Выбранные бронирования подтверждены.")
    
    mark_as_confirmed.short_description = "Подтвердить выбранные бронирования"

    def mark_as_cancelled(self, request, queryset):
        """Отметить бронирование как отменённое"""
        queryset.update(status="cancelled")
        self.message_user(request, "Выбранные бронирования отменены.")

    mark_as_cancelled.short_description = "Отменить выбранные бронирования"
