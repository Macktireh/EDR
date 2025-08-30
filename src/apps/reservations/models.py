from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.common.models import BaseModel


class Destination(BaseModel):
    """Ville de départ ou d'arrivée."""

    name = models.CharField(verbose_name=_("City name"), max_length=128)
    country = models.CharField(verbose_name=_("Country name"), max_length=128)

    class Meta:
        db_table = "destination"
        verbose_name = _("Destination")
        verbose_name_plural = _("Destinations")

    def __str__(self) -> str:
        return self.name


class Passenger(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("User"), related_name="passenger", null=True
    )
    name = models.CharField(_("Full name"), max_length=128)
    email = models.EmailField(_("email address"))
    phone_number = models.CharField(verbose_name=_("Phone Number"), max_length=24, null=True)
    birth_date = models.DateField(verbose_name=_("Date of birth"), null=True)
    identity_document = models.FileField(
        verbose_name=_("Identity document"), upload_to="passports/", null=True
    )

    class Meta:
        db_table = "passengers"
        verbose_name = _("Passenger")
        verbose_name_plural = _("Passengers")

    def __str__(self) -> str:
        return f"Passenger: {self.name or self.user}"


class Price(BaseModel):
    departure_city = models.ForeignKey(
        Destination,
        related_name="prices_departures",
        verbose_name=_("Departure city"),
        on_delete=models.CASCADE,
    )
    arrival_city = models.ForeignKey(
        Destination,
        related_name="prices_arrivals",
        verbose_name=_("Arrival city"),
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(verbose_name=_("Price"), max_digits=10, decimal_places=2)

    class Meta:
        db_table = "price"
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")

    def __str__(self) -> str:
        return f"{self.departure_city} → {self.arrival_city} ({self.price})"


class Reservation(BaseModel):
    """Réservation effectuée par un utilisateur."""

    class TicketType(models.TextChoices):
        ONE_WAY = "one_way", _("One-way ticket")
        ROUND_TRIP = "round_trip", _("Round-trip ticket")

    passengers = models.ManyToManyField(
        Passenger, verbose_name=_("Passengers"), related_name="reservations"
    )
    ticket_type = models.CharField(
        verbose_name=_("Ticket type"),
        max_length=24,
        choices=TicketType.choices,
        default=TicketType.ONE_WAY,
    )
    total_amount = models.DecimalField(
        verbose_name=_("Total amount"), max_digits=10, decimal_places=2
    )

    class Meta:
        db_table = "reservations"
        verbose_name = _("Reservation")
        verbose_name_plural = _("Reservations")

    def __str__(self) -> str:
        return f"Reservation {self.id} - {self.ticket_type}"  # type: ignore


class Luggage(BaseModel):
    """Options de bagages associées à une réservation."""

    class WeightCategory(models.TextChoices):
        KG_0_10 = "0-10", _("0 to 10 kg (inclusive)")
        KG_11_20 = "11-20", _("11 to 20 kg")
        KG_21_30 = "21-30", _("21 to 30 kg")
        KG_31_40 = "31-40", _("31 to 40 kg")
        ABOVE_40 = "40+", _("+40 kg")

    category = models.CharField(
        verbose_name=_("Category"),
        max_length=20,
        choices=WeightCategory.choices,
        default=WeightCategory.KG_0_10,
    )
    extra_fee = models.DecimalField(
        verbose_name=_("Extra fee"),
        max_digits=10,
        decimal_places=2,
        default=0,  # type: ignore
    )

    class Meta:
        db_table = "luggage"
        verbose_name = _("Luggage")
        verbose_name_plural = _("Luggage")

    def __str__(self) -> str:
        return f"Luggage: {self.category}"


class Travel(BaseModel):
    """Un trajet spécifique (ex: Djibouti -> Dire Dawa)."""

    departure_city = models.ForeignKey(
        Destination,
        related_name="departures",
        verbose_name=_("Departure city"),
        on_delete=models.CASCADE,
    )
    arrival_city = models.ForeignKey(
        Destination,
        related_name="arrivals",
        verbose_name=_("Arrival city"),
        on_delete=models.CASCADE,
    )
    departure_date = models.DateField(verbose_name=_("Departure date"))
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, verbose_name=_("Reservation")
    )
    luggage = models.OneToOneField(
        Luggage, on_delete=models.CASCADE, verbose_name=_("Luggage"), null=True
    )

    class Meta:
        db_table = "travel"
        verbose_name = _("Travel")
        verbose_name_plural = _("Travel")

    def __str__(self) -> str:
        return f"{self.departure_city} → {self.arrival_city} ({self.departure_date})"
