from django.db import models
from django.conf import settings

from order_status.models import OrderStatus
from user.models import User


# Create your models here.
class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    order_status = models.ForeignKey(to=OrderStatus, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(decimal_places=2, max_digits=10)
    confirmation_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']