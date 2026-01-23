from django.db import models
from django.conf import settings

from user.models import User


# Create your models here.
class Cart(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)