from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payments.models import Invoice, Payment, Ticket


# @receiver(post_save, sender=Payment)
# def handle_payment(sender, instance: Payment, created: bool, **kwargs) -> None:
#     """Handle payment creation and update logic."""
#     if instance.status == Payment.PaymentStatus.PAID:
#         # Generate invoice only if payment is made online
#         if instance.method != Payment.PaymentMethod.CASH:
#             Invoice.objects.get_or_create(
#                 reservation=instance.reservation,
#             )

#         Ticket.objects.get_or_create(
#             reservation=instance.reservation,
#         )
