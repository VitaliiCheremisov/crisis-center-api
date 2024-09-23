# Модуль админки модели пожертвований Cloudpayment.
from django.conf import settings
from django.contrib import admin

from .models import CloudPayment


@admin.register(CloudPayment)
class CloudPaymentAdmin(admin.ModelAdmin):
    """Админ зона пожертвований Cloudpayment"""

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
    list_filter = ("pub_date", "status")
