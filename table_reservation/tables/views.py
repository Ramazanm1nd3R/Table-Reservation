from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from .models import Table, Reservation
from .serializers import TableSerializer, ReservationSerializer

class TableListView(generics.ListAPIView):
    """Список всех столиков с фильтрацией"""
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        seats = self.request.query_params.get("seats")
        table_type = self.request.query_params.get("type")

        if seats:
            queryset = queryset.filter(seats__gte=seats)
        if table_type:
            queryset = queryset.filter(table_type=table_type)

        return queryset


class CreateReservationView(generics.CreateAPIView):
    """Создание бронирования столика"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CancelReservationView(generics.UpdateAPIView):
    """Отмена бронирования (не позднее чем за 30 минут до начала)"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        
        if reservation.is_cancellable():
            reservation.status = "cancelled"
            reservation.save()
            return Response({"message": "Бронирование отменено."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Отменить можно не позднее, чем за 30 минут до начала."}, status=status.HTTP_400_BAD_REQUEST)


class ConfirmReservationView(generics.UpdateAPIView):
    """Подтверждение бронирования за 15 минут до начала"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()

        if reservation.is_confirmable():
            reservation.status = "confirmed"
            reservation.save()
            return Response({"message": "Бронирование подтверждено."}, status=status.HTTP_200_OK)

        return Response({"error": "Вы не можете подтвердить бронирование сейчас."}, status=status.HTTP_400_BAD_REQUEST)
