from django.db import models
from django.conf import settings
from django.utils.timezone import now, timedelta

class Table(models.Model):
    """Модель столика"""
    TYPE_CHOICES = [
        ("regular", "Обычный"),
        ("vip", "VIP"),
        ("window", "У окна"),
    ]

    number = models.PositiveIntegerField(unique=True)  # Уникальный номер столика
    seats = models.PositiveIntegerField()  # Количество мест
    table_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="regular")  # Тип столика
    is_available = models.BooleanField(default=True)  # Доступность столика

    def __str__(self):
        return f"Столик {self.number} ({self.get_table_type_display()})"


class Reservation(models.Model):
    """Модель бронирования столика"""
    STATUS_CHOICES = [
        ("pending", "Ожидает подтверждения"),
        ("confirmed", "Подтверждено"),
        ("cancelled", "Отменено"),
        ("expired", "Истекло"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="reservations")
    reservation_time = models.DateTimeField()  # Дата и время бронирования
    duration = models.PositiveIntegerField(default=60)  # Длительность брони (минуты)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["table", "reservation_time"], name="unique_reservation_time"),
        ]

    def is_cancellable(self):
        """Проверяем, можно ли отменить (за 30 минут до начала)"""
        return now() < self.reservation_time - timedelta(minutes=30)

    def is_confirmable(self):
        """Бронирование должно быть подтверждено за 15 минут до начала"""
        return now() >= self.reservation_time - timedelta(minutes=15)

    def __str__(self):
        return f"Бронь {self.table} на {self.reservation_time} ({self.get_status_display()})"
