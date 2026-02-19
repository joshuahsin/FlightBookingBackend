from django.db import models

from cabin_class.models import CabinClass
from flight.models import Flight


# Create your models here.
class Seat(models.Model):
    id = models.BigAutoField(primary_key=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    cabin_class = models.ForeignKey(CabinClass, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=3)
    occupied = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['flight', 'seat_number'],
                name='unique_seat_per_flight_cabin'
            )
        ]