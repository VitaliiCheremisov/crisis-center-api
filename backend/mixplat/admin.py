# Модуль админки модели платежа Mixplat.
from django.conf import settings
from django.contrib import admin

from .models import MixPlat


@admin.register(MixPlat)
class DonationAdmin(admin.ModelAdmin):
    """Админ зона платежа Mixplat."""

    list_display = (
        "email",
        "donat",
        "custom_donat",
        "payment_method",
        "monthly_donat",
        "subscription",
        "pub_date",
        "payment_id",
        "status",
        "user_account_id",
        "date_created",
        "date_processed",
        "payment_operator",
    )
    empty_value_display = settings.EMPTY_VALUE
    list_filter = ("-pub_date", "payment_status")
