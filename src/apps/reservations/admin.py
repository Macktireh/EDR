from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.reservations.models import Destination, Luggage, Passenger, Price, Reservation, Travel


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("price", "departure_city", "arrival_city", "created_at", "updated_at")
    search_fields = ("departure_city", "arrival_city",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = (
        "departure_city",
        "arrival_city",
        "departure_date",
        "luggage",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "departure_date",
        "departure_city",
        "arrival_city",
    )
    search_fields = (
        "departure_city__name",
        "arrival_city__name",
    )
    ordering = ("-departure_date", "departure_city")
    date_hierarchy = "departure_date"
    readonly_fields = ("created_at", "updated_at")

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone_number",
        "birth_date",
        "created_at",
        "updated_at",
    )
    list_filter = ("birth_date",)
    search_fields = (
        "name",
        "email",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket_type",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "ticket_type",
        "created_at",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            _("Passenger information"),
            {"fields": ("passengers",)},
        ),
        (
            _("Ticket details and pricing"),
            {"fields": ("ticket_type", "total_amount",)},
        ),
        (
            _("Dates"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(Luggage)
class LuggageAdmin(admin.ModelAdmin):
    list_display = (
        "category",
        "extra_fee",
    )
    list_filter = ("category",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
