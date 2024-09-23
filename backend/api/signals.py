# from django.dispatch import receiver
# from django.db.models.signals import post_save
#
# from .utils import send_payment_email
# from cloudpayments.models import CloudPayment
# from mixplat.models import MixPlat
#
#
# @receiver(post_save, sender=CloudPayment)
# @receiver(post_save, sender=MixPlat)
# def payment_handler(sender, instance, **kwargs):
#     email = instance.email
#     message = None
#     declined_statuses = ["Declined", "Cancelled", "failure"]
#
#     if instance.status in declined_statuses:
#         message = f"Ваш платеж на {instance.donat} был отклонен."
#     elif instance.status in ["success", "Completed"]:
#         message = f"Ваш платеж на {instance.donat} выполнен."
#
#     if email and message:
#         send_payment_email(email, message)
