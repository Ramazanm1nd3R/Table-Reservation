from django.urls import path
from .views import (
    TableListView, CreateReservationView, CancelReservationView,
    ConfirmReservationView, ConfirmReservationEmailView
)

urlpatterns = [
    path("tables/", TableListView.as_view(), name="table-list"),
    path("reserve/", CreateReservationView.as_view(), name="create-reservation"),
    path("cancel/<int:pk>/", CancelReservationView.as_view(), name="cancel-reservation"),
    path("confirm/<int:pk>/", ConfirmReservationView.as_view(), name="confirm-reservation"),
    path("confirm-email/<str:token>/", ConfirmReservationEmailView.as_view(), name="confirm-reservation-email"),  # ✅ Новый endpoint
]
