from django.urls import path

from apps.reservations.views import (
    ConfirmReservationView,
    DestinationSearchView,
    PaymentMethodView,
    ReservationDoneView,
    ReservationView,
)

app_name = "reservation"

urlpatterns = [
    path("", ReservationView.as_view(), name="form"),
    path("payment-method", PaymentMethodView.as_view(), name="payment_method"),
    path("confirm", ConfirmReservationView.as_view(), name="confirm"),
    path("done", ReservationDoneView.as_view(), name="done"),
    path("destination-search", DestinationSearchView.as_view(), name="destination_search"),
]
