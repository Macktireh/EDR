from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as AuthGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as AuthGroup
from django.utils.translation import gettext_lazy as _

from apps.accounts.forms import UserChangeForm, UserCreationForm
from apps.accounts.models import Group, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = (
        "email",
        "name",
        "is_active",
        "email_confirmed",
        "is_staff",
        "is_superuser",
        "date_joined",
        "updated_at",
    )
    list_filter = (
        "is_superuser",
        "is_staff",
        "is_active",
        "email_confirmed",
        "date_joined",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            _("Personal info"),
            {"fields": ("name",)},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "email_confirmed",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "updated_at",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "email_confirmed",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
    readonly_fields = ("date_joined", "last_login", "updated_at")
    search_fields = (
        "email",
        "name",
    )
    ordering = ("date_joined",)


admin.site.unregister(AuthGroup)


@admin.register(Group)
class GroupAdmin(AuthGroupAdmin):
    pass
