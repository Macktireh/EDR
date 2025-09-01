from datetime import date
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.decorators import login_not_required  # type: ignore
from django.db import transaction
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.common.types import HttpRequest
from apps.payments.models import Payment, ReservationNotice
from apps.reservations.forms import PaymentMethodForm, ReservationForm
from apps.reservations.models import Destination, Luggage, Passenger, Price, Reservation
from apps.reservations.utils import (
    PayloadEmail,
    attach_temp_document,
    delete_file_temporarily,
    save_file_temporarily,
    send_email,
)


@method_decorator(decorator=login_not_required, name="dispatch")
class ReservationView(View):
    template_name = "pages/reservation.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": ReservationForm()}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = ReservationForm(data=request.POST or None, files=request.FILES or None)
        reservation_data = request.session.get("reservation_data")
        if reservation_data:
            delete_file_temporarily(reservation_data["id"], reservation_data["file_name"])
            request.session.delete("reservation_data")

        if form.is_valid():
            data = form.cleaned_data
            for key, value in data.items():
                if isinstance(value, date):
                    data[key] = value.isoformat()

            data["id"] = uuid4().hex
            if data.get("return_date"):
                data["ticket_type"] = Reservation.TicketType.ROUND_TRIP
            else:
                data["ticket_type"] = Reservation.TicketType.ONE_WAY
            identity_document = data.get("identity_document")
            if identity_document:
                save_file_temporarily(data["id"], identity_document)
                data["file_name"] = data["identity_document"].name
                del data["identity_document"]

            request.session["reservation_data"] = data
            return redirect("reservation:payment_method")
        return render(request=request, template_name=self.template_name, context={"form": form})


@method_decorator(decorator=login_not_required, name="dispatch")
class PaymentMethodView(View):
    template_name = "pages/payment_method.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        data = request.session.get("reservation_data")
        if not data:
            return redirect("reservation:form")

        prices = Price.objects.get(
            departure_city__name=data["departure_city"],
            arrival_city__name=data["arrival_city"],
        )
        total_amount = 0
        if data["ticket_type"] == Reservation.TicketType.ONE_WAY:
            total_amount = prices.price
        else:
            total_amount = prices.price * 2

        luggage = Luggage.objects.get(category=data["luggage"])
        total_amount += luggage.extra_fee
        data["total_amount"] = float(total_amount)
        request.session["reservation_data"] = data

        context = {
            "form": PaymentMethodForm(),
            "data": data,
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = PaymentMethodForm(data=request.POST or None)

        if form.is_valid():
            reservation_data = request.session.get("reservation_data")
            reservation_data["payment_method"] = form.cleaned_data["payment_method"]  # type: ignore
            # delete_file_temporarily(reservation_data["id"], reservation_data["file_name"])
            # request.session.pop("reservation_data", None)
            request.session["reservation_data"] = reservation_data
            return redirect("reservation:confirm")
        return render(request=request, template_name=self.template_name, context={"form": form})


@method_decorator(decorator=login_not_required, name="dispatch")
class ConfirmReservationView(View):
    template_name = "pages/confirm_reservation.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        data = request.session.get("reservation_data")
        if not data:
            return redirect("reservation:form")

        luggage = Luggage.objects.get(category=data["luggage"])
        data["payment_method"] = Payment.PaymentMethod(data["payment_method"]).label

        context = {
            "data": data,
            "luggage": luggage,
        }
        return render(request, self.template_name, context)

    def post(
        self, request: HttpRequest
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect | HttpResponse | None:
        print("-" * 70)
        print()
        print("Reservation Confirm view")

        data = request.session.get("reservation_data")
        if not data:
            return redirect("reservation:form")

        try:
            print("In transaction")
            with transaction.atomic():
                passenger = Passenger(
                    name=data["name"],
                    email=data["email"],
                    phone_number=f"{data['country_code']} {data['phone_number']}",
                    birth_date=data["birth_date"],
                )

                # rattacher le fichier d’identité avant le save
                attach_temp_document(
                    data,
                    lambda file_obj, file_name: passenger.identity_document.save(
                        file_name, file_obj, save=False
                    ),
                )

                passenger.save()

                # Créer la réservation
                reservation = Reservation.objects.create(
                    ticket_type=data.get("ticket_type", Reservation.TicketType.ONE_WAY),
                    total_amount=Decimal(data.get("total_amount", "0.00")),
                )

                # Lier le passenger à la réservation
                reservation.passengers.add(passenger)
                reservation_notice = ReservationNotice.objects.create(reservation=reservation)
                data["payment_method"] = Payment.PaymentMethod(data["payment_method"]).label
                context = {
                    "reservation": data,
                    "reservation_notice": reservation_notice,
                    "passenger": passenger,
                }
                body = render_to_string("mail/reservation_notice.txt", context=context)
                html_body = render_to_string("mail/reservation_notice.html", context=context)
                html_attach_file = render_to_string("pdf/reservation_notice.html", context=context)
                payload = PayloadEmail(
                    subject=_("EDR Reservation Notice – Payment pending"),
                    body=body,
                    to=[passenger.email],
                    html=html_body,
                    html_attach_file=html_attach_file,
                )  # type: ignore
                transaction.on_commit(lambda: send_email(payload))

            request.session.pop("reservation_data", None)
            delete_file_temporarily(data["id"], data["file_name"])
            print()
            print("-" * 70)
            return redirect("reservation:done")
        except Exception as e:
            raise e
            luggage = Luggage.objects.get(category=data["luggage"])
            data["payment_method"] = Payment.PaymentMethod(data["payment_method"]).label

            context = {
                "data": data,
                "luggage": luggage,
            }
            print()
            print("-" * 70)
            return render(request=request, template_name=self.template_name, context=context)


@method_decorator(decorator=login_not_required, name="dispatch")
class ReservationDoneView(View):
    template_name = "pages/reservation_done.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


@method_decorator(decorator=login_not_required, name="dispatch")
class DestinationSearchView(View):
    template_name = "partials/autocompletion.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.htmx:
            return HttpResponseBadRequest("only htmx supported")
        search = request.GET.get("q")
        if not search:
            return HttpResponseBadRequest("Missing search parameter 'q'")
        destinations = Destination.objects.filter(name__icontains=search)[:10]
        context = {
            "destinations": destinations,
        }
        return render(request, self.template_name, context)
