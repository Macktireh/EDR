from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name=_("Created at"),
        auto_now_add=True,
        editable=True,
        help_text=_("Date time on which the object was created."),
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated at"),
        auto_now=True,
        editable=True,
        help_text=_("Date time on which the object was updated."),
    )

    class Meta:
        abstract = True
