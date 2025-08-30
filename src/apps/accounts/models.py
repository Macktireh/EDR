from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as AuthGroup
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager
from apps.common.models import BaseModel


class User(BaseModel, AbstractUser):
    username = None
    first_name = None
    last_name = None
    created_at = None
    name = models.CharField(verbose_name=_("Full name"), max_length=128)
    email = models.EmailField(verbose_name=_("email address"), unique=True, db_index=True)
    email_confirmed = models.BooleanField(default=False)
    phone_number = models.CharField(verbose_name=_("Phone Number"), max_length=24, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "name",
    ]

    objects = UserManager()  # type: ignore

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.name

    def get_full_name(self) -> str:
        return self.name


class Group(AuthGroup):
    class Meta:
        proxy = True
