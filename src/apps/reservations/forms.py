from datetime import date, datetime, timedelta

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.common.validators import FileValidator
from apps.payments.models import Payment
from apps.reservations.models import Destination, Luggage

ERROR_MESSAGES = {
    "required": _("This field is required."),
    "invalid_date": _("Invalid date format. Use YYYY-MM-DD."),
    "invalid_email": _("Invalid email format."),
    "file_too_large": _("The file is too large (max 2MB allowed)."),
    "invalid_file_format": _("Invalid file format. Only PDF, PNG, JPG are accepted."),
}

DEFAULT_TEXT_WIDGET = forms.TextInput(attrs={"class": "grow"})
DEFAULT_DATE_WIDGET = forms.DateInput(attrs={"type": "date", "class": "grow"})


class EvenOddDateValidationMixin:
    """Validation pair/impair selon pays avec suggestions"""

    def get_suggestions(self, date_field: date) -> list[date]:
        """Retourne la date valide précédente et suivante."""
        suggestions = []
        today = date.today()

        # Jour précédent
        prev_day = date_field - timedelta(days=1)
        if prev_day >= today:
            suggestions.append(prev_day)

        # Jour suivant
        next_day = date_field + timedelta(days=1)
        if next_day >= today:
            suggestions.append(next_day)

        return suggestions

    def validate_city_date(self, city_name: str, date_field: date, context: str):
        dest = Destination.objects.filter(name=city_name).first()
        if not dest or not date_field:
            return

        # Vérif Djibouti (jours pairs seulement)
        if dest.country == "Djibouti" and date_field.day % 2 != 0:
            suggestions = self.get_suggestions(date_field)
            msg = _(f"{context.capitalize()}s to Djibouti are only available on even days.")
            if suggestions:
                sugg_str = ", ".join([d.strftime("%d/%m/%Y") for d in suggestions])
                msg += _(" You may choose instead: ") + sugg_str
            raise forms.ValidationError(msg)

        # Vérif Ethiopia (jours impairs seulement)
        if dest.country == "Ethiopia" and date_field.day % 2 == 0:
            suggestions = self.get_suggestions(date_field)
            msg = _(f"{context.capitalize()}s from Ethiopia are only available on odd days.")
            if suggestions:
                sugg_str = ", ".join([d.strftime("%d/%m/%Y") for d in suggestions])
                msg += _(" You may choose instead: ") + sugg_str
            raise forms.ValidationError(msg)


class BaseReservationForm(forms.Form, EvenOddDateValidationMixin):
    """Form de base avec outils communs"""


class ReservationForm(BaseReservationForm):
    departure_city = forms.CharField(
        initial="Djibouti",
        label=_("Departure city"),
        error_messages={"required": _("Please enter the departure city.")},
        widget=DEFAULT_TEXT_WIDGET,
    )
    arrival_city = forms.CharField(
        initial="Dire Dawa",
        label=_("Arrival city"),
        error_messages={"required": _("Please enter the arrival city.")},
        widget=DEFAULT_TEXT_WIDGET,
    )
    departure_date = forms.DateField(
        # initial=date.today() + timedelta(days=1),
        label=_("Departure date"),
        error_messages={
            "required": _("Please select your departure date."),
            "invalid": ERROR_MESSAGES["invalid_date"],
        },
        widget=DEFAULT_DATE_WIDGET,
    )
    return_date = forms.DateField(
        # initial=lambda: date.today() + timedelta(days=10),
        required=False,
        label=_("Return date"),
        error_messages={"invalid": ERROR_MESSAGES["invalid_date"]},
        widget=DEFAULT_DATE_WIDGET,
    )
    name = forms.CharField(
        # initial="Mack As",
        label=_("Full name"),
        error_messages={"required": _("Please provide your full name.")},
        widget=forms.TextInput(
            attrs={"class": "grow", "placeholder": _("e.g.: Ali Ahmed")}
        )
    )
    email = forms.EmailField(
        # initial="mack@example.com",
        label=_("Email"),
        error_messages={
            "required": _("Please provide your email address."),
            "invalid": ERROR_MESSAGES["invalid_email"],
        },
        widget=forms.TextInput(
            attrs={"class": "grow", "placeholder": _("e.g.: ali.ahmed@example.com")}
        )
    )
    country_code = forms.ChoiceField(
        choices=[
            ("+253", "Djibouti (+253)"),
            ("+251", "Ethiopia (+251)"),
        ],
        label=_("Country code"),
        error_messages={"required": _("Please select your country code.")},
        widget=forms.Select(attrs={"class": "select select-ghost w-fit text-xs"}),
    )
    phone_number = forms.CharField(
        # initial="77999999",
        label=_("Phone number"),
        error_messages={"required": _("Please provide your phone number.")},
        widget=forms.TextInput(
            attrs={"type": "tel", "class": "grow", "placeholder": _("e.g.: 77999999")}
        ),
    )
    birth_date = forms.DateField(
        # initial=date(1999, 2, 14),
        required=False,
        label=_("Date of birth"),
        error_messages={"invalid": ERROR_MESSAGES["invalid_date"]},
        widget=DEFAULT_DATE_WIDGET,
    )
    identity_document = forms.FileField(
        label=_("Identity document"),
        help_text=_("Max size 2MB. Accepted formats: PDF, PNG, JPG."),
        validators=[
            FileValidator(
                allowed_extensions=["jpg", "jpeg", "png", "pdf"],
                max_size=2 * 1024 * 1024,  # 2 MB
            )
        ],
        widget=forms.FileInput(
            attrs={
                "type": "file",
                "class": "file-input file-input-ghost w-full",
                "placeholder": _(
                    "Please attach your identity document (passport or identity card)."
                ),
            }
        ),
    )
    luggage = forms.ChoiceField(
        initial=Luggage.WeightCategory.KG_0_10,
        choices=Luggage.WeightCategory.choices,
        error_messages={"required": _("Please select your luggage weight category.")},
        widget=forms.RadioSelect(attrs={"class": "radio"}),
    )

    @property
    def luggages(self):
        return Luggage.objects.all()

    def clean_departure_city(self):
        city = self.cleaned_data.get("departure_city")
        if not Destination.objects.filter(name=city).exists():
            raise forms.ValidationError(
                _("The departure city '%(city)s' is not available in our destinations."),
                params={"city": city},
            )
        return city

    def clean_arrival_city(self):
        dep = self.cleaned_data.get("departure_city")
        arr = self.cleaned_data.get("arrival_city")

        if not Destination.objects.filter(name=arr).exists():
            raise forms.ValidationError(
                _("The arrival city '%(city)s' is not available in our destinations."),
                params={"city": arr},
            )
        if dep == arr:
            raise forms.ValidationError(_("Arrival city cannot be the same as departure city."))
        return arr

    def clean_departure_date(self):
        dep_date = self.cleaned_data.get("departure_date")
        dep_city = self.cleaned_data.get("departure_city")
        today = date.today()

        if dep_date and dep_date < today:
            raise forms.ValidationError(_("Departure date cannot be in the past."))

        # réservation min 6h avant (train 9h)
        now = datetime.now()
        if dep_date == today and now.hour >= 3:
            raise forms.ValidationError(
                _(
                    "Reservations must be made at least 6 hours before departure "
                    "(train leaves at 9 AM)."
                )
            )

        self.validate_city_date(dep_city, dep_date, "departure")  # type: ignore
        return dep_date

    def clean_return_date(self):
        dep_date = self.cleaned_data.get("departure_date")
        ret_date = self.cleaned_data.get("return_date")
        arr_city = self.cleaned_data.get("arrival_city")

        if dep_date and ret_date:
            if ret_date <= dep_date:
                self.add_error("return_date", _("Return date must be after the departure date."))
            else:
                self.validate_city_date(arr_city, ret_date, "return")  # type: ignore
        return ret_date


class PaymentMethodForm(BaseReservationForm):
    payment_method = forms.ChoiceField(
        choices=Payment.PaymentMethod.choices,
        error_messages={"required": _("Please select your payment method.")},
    )

    @property
    def payment_methods(self) -> list[dict[str, str]]:
        return [
            {"value": method[0], "label": method[1], "id": f"payment_method-{method[0]}"}
            for method in Payment.PaymentMethod.choices
        ]
