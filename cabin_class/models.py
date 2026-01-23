from django.db import models

# Create your models here.
class CabinClass(models.Model):
    id = models.BigAutoField(primary_key=True)
    cabin_class_name = models.CharField(max_length=100)
    baggage_allowance = models.IntegerField(default=0)
    refundable = models.BooleanField(default=False)