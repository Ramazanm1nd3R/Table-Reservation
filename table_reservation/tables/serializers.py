from rest_framework import serializers
from .models import Table, Reservation
from django.utils.timezone import now, timedelta

class TableSerializer(serializers.ModelSerializer):
    """ Сериалайзер для столика """

    class Meta:
        model = Table
        fields = "__all__"

class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Reservation
        fields = ["id", "user", "table", "reservation_time", "duration", "status"]

    def validate(self, data):
        """Валидация бронирования"""
        user = self.context["request"].user
        reservation_time = data.get("reservation_time")
        table = data.get("table")

        # Проверка на активные бронирования (макс. 3)
        active_reservations = Reservation.objects.filter(user=user, status__in=["pending", "confirmed"]).count()
        if active_reservations >= 3:
            raise serializers.ValidationError("Вы не можете иметь больше 3 активных бронирований.")

        # Проверяем доступность столика
        if Reservation.objects.filter(table=table, reservation_time=reservation_time, status="confirmed").exists():
            raise serializers.ValidationError("Этот столик уже забронирован на указанное время.")

        return data