from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from .models import Table, Reservation
from .serializers import TableSerializer, ReservationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.urls import reverse
from users.utils import Util
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
import secrets
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


class ConfirmReservationEmailView(APIView):
    """Подтверждение бронирования через email"""

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            reservation = Reservation.objects.get(pk=uid)

            if default_token_generator.check_token(reservation, token):
                reservation.status = "confirmed"
                reservation.save()
                return Response({"message": "Бронирование подтверждено!"}, status=status.HTTP_200_OK)
            
            return Response({"error": "Неверный токен"}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, Reservation.DoesNotExist):
            return Response({"error": "Некорректная ссылка"}, status=status.HTTP_400_BAD_REQUEST)
        
class ConfirmReservationView(generics.GenericAPIView):
    """Подтверждение бронирования через email"""
    serializer_class = ReservationSerializer

    def get(self, request, uidb64, token):
        try:
            # Декодируем ID брони
            reservation_id = urlsafe_base64_decode(uidb64).decode()
            reservation = Reservation.objects.get(pk=reservation_id, confirmation_token=token)

            if reservation.is_confirmable():
                reservation.status = "confirmed"
                reservation.confirmation_token = secrets.token_urlsafe(32)  # Меняем токен на новый
                reservation.save()
                return Response({"message": "Бронирование подтверждено!"}, status=status.HTTP_200_OK)

            return Response({"error": "Срок подтверждения истёк."}, status=status.HTTP_400_BAD_REQUEST)

        except (ObjectDoesNotExist, ValueError, TypeError):
            return Response({"error": "Некорректная ссылка."}, status=status.HTTP_400_BAD_REQUEST)
        

class CreateReservationView(generics.CreateAPIView):
    """Создание бронирования с отправкой email"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        reservation = serializer.save(user=self.request.user)

        # Формируем ссылку для подтверждения
        confirm_url = self.request.build_absolute_uri(
            reverse("confirm-reservation-email", args=[reservation.confirmation_token])
        )

        #  Формируем email-сообщение
        email_data = {
            "email_subject": "Подтверждение бронирования",
            "email_body": f"""
            Здравствуйте, {self.request.user.email}!

            Вы забронировали столик на {reservation.reservation_time}. 

            Для подтверждения бронирования, пожалуйста, перейдите по ссылке:
            {confirm_url}

            Если вы не подтвердите бронирование за 15 минут до начала, оно будет отменено.

            Спасибо за использование нашего сервиса!
            """,
            "to_email": [self.request.user.email],
        }

        # Отправляем email
        Util.send_email(email_data)

        return Response({"message": "Бронирование создано. Проверьте почту для подтверждения."}, status=status.HTTP_201_CREATED)
