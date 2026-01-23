from django.db import models


# Create your models here.

class BookingStatus(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    is_terminal = models.BooleanField(default=False)
