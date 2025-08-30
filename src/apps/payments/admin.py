from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.payments.models import Invoice, Payment, ReservationNotice, Ticket


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reservation",
        "method",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = (
        "method",
        "status",
        "created_at",
    )
    search_fields = (
        "reservation__user__email",
        "reservation__name",
        "reservation__travel__id",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            _("Payment details"),
            {"fields": ("reservation", "method", "status", "total_amount")},
        ),
        (
            _("Dates"),
            {"fields": ("created_at", "updated_at")},
        ),
    )

    def total_amount(self, obj: Payment):
        return obj.reservation.total_amount


@admin.register(ReservationNotice)
class ReservationNoticeAdmin(admin.ModelAdmin):
    list_display = ("reservation", "notice_number", "total_amount")
    search_fields = ("notice_number", "reservation__name", "reservation__user__email")
    readonly_fields = ("notice_number", "html_string")

    def total_amount(self, obj: Invoice):
        return obj.reservation.total_amount


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("reservation", "invoice_number", "total_amount")
    search_fields = ("invoice_number", "reservation__name", "reservation__user__email")
    readonly_fields = ("invoice_number", "html_string")

    def total_amount(self, obj: ReservationNotice):
        return obj.reservation.total_amount


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "reservation",
        "ticket_number",
        "issued_at",
        "is_active",
    )
    list_filter = ("is_active", "issued_at")
    search_fields = ("ticket_number", "reservation__name", "reservation__user__email")
    ordering = ("-issued_at",)
    readonly_fields = ("ticket_number", "issued_at", "is_active", "html_string")
