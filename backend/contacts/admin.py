# Модуль админки модели контакты.
from django.conf import settings
from django.contrib import admin

from .models import Contact, Donor


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Админ зона контактов."""

    list_display = ("username", "email", "subject", "comment")
    empty_value_display = settings.EMPTY_VALUE
    list_filter = ("username",)


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    """Админ зона доноров."""

    list_display = ("email", "subscription", "count_declined")
    empty_value_display = settings.EMPTY_VALUE
    list_filter = ("email", "subscription", "count_declined")
