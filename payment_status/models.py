from django.db import models

# Create your models here.
class PaymentStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=30, unique=True)
    is_terminal = models.BooleanField(default=False)