from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from users.forms import UserChangeForm, UserCreationForm
from users.models import User
from utils.mixins import ExportCsvMixin

admin.site.unregister(Group)


class UserAdmin(DjangoUserAdmin, ExportCsvMixin):
    fieldsets = (
        (None, {"fields": ("username", "email")}),
        (
            _("Personal info"),
            {"fields": ("full_name", "bio", "country", "date_of_birth")},
        ),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    actions = ["export_as_csv"]
    list_per_page = 20

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("username", "email", "full_name", "is_staff")
    list_filter = ("is_superuser", "is_active")
    search_fields = ("username", "full_name", "email")
    ordering = ("-date_joined",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
