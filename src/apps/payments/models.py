from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.reservations.models import Reservation


def generate_short_uuid() -> str:
    return uuid4().hex[:16].upper()
    # return f"{prefix + "-" if prefix else ""}{uuid4().hex[:16].upper()}"


class Payment(BaseModel):
    """Paiement lié à une réservation."""

    class PaymentMethod(models.TextChoices):
        CASH = "cash", _("Cash")
        WAAFI = "waafi", _("Waafi")
        CAC = "cac", _("Cac Pay")
        SABA = "saba", _("Saba Pay")
        BOA = "boa", _("Boa Pay")
        BCI = "bci", _("BCI Pay")

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("On hold")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")
        CANCELED = "canceled", _("Canceled")

    reservation = models.OneToOneField(
        Reservation, on_delete=models.CASCADE, verbose_name=_("Reservation")
    )
    method = models.CharField(
        verbose_name=_("Method"), max_length=20, choices=PaymentMethod.choices
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    class Meta:
        db_table = "payments"
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self) -> str:
        return f"Payment {self.id} - {self.method} - {self.status}"  # type: ignore


class ReservationNotice(models.Model):
    reservation = models.OneToOneField(
        Reservation, on_delete=models.CASCADE, verbose_name=_("Reservation")
    )
    notice_number = models.CharField(
        verbose_name=_("Reservation notice number"),
        max_length=24,
        unique=True,
        default=generate_short_uuid,
    )
    html_string = models.TextField(
        verbose_name=_("HTML String"),
        help_text=_("HTML content of the reservation notice"),
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "reservation_notices"
        verbose_name = _("Reservation notice")
        verbose_name_plural = _("Reservation notices")

    def __str__(self) -> str:
        return f"Avis {self.notice_number} - Reservation {self.reservation.id}"  # type: ignore


class Invoice(models.Model):
    reservation = models.OneToOneField(
        Reservation, on_delete=models.CASCADE, verbose_name=_("Reservation")
    )
    invoice_number = models.CharField(
        verbose_name=_("invoice number"),
        max_length=24,
        unique=True,
        default=generate_short_uuid,
    )
    html_string = models.TextField(
        verbose_name=_("HTML String"),
        help_text=_("HTML content of the invoice"),
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "invoices"
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def __str__(self) -> str:
        return f"Facture {self.invoice_number} - {self.reservation}"


class Ticket(models.Model):
    reservation = models.OneToOneField(
        Reservation, on_delete=models.CASCADE, verbose_name=_("Reservation")
    )
    ticket_number = models.CharField(
        verbose_name=_("ticket number"),
        max_length=24,
        unique=True,
        default=generate_short_uuid,
    )
    issued_at = models.DateTimeField(verbose_name=_("Issued at"), auto_now_add=True)
    is_active = models.BooleanField(verbose_name=_("active"), default=True)
    html_string = models.TextField(
        verbose_name=_("HTML String"),
        help_text=_("HTML content of the ticket"),
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "tickets"
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self) -> str:
        return f"Billet {self.ticket_number} - {self.reservation}"
