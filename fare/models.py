from django.db import models

from cabin_class.models import CabinClass
from flight.models import Flight


# Create your models here.
class Fare(models.Model):
    id = models.BigAutoField(primary_key=True)
    flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE)
    cabin_class = models.ForeignKey(to=CabinClass, on_delete=models.CASCADE)
    fare_price = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    #change_fee = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    seats_available = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['flight', 'cabin_class'],
                name='unique_fare_per_flight_cabin'
            )
        ]