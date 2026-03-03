from django.db import models

from order.models import Order
from payment_status.models import PaymentStatus
from user.models import User


# Create your models here.

class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    stripe_payment_session_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.ForeignKey(to=PaymentStatus, on_delete=models.SET_NULL, null=True)
    payment_date_time = models.DateTimeField(blank=True, null=True, default=None)
