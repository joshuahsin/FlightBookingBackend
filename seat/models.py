from django.db import models

from cabin_class.models import CabinClass
from flight.models import Flight


# Create your models here.
class Seat(models.Model):
    id = models.BigAutoField(primary_key=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    cabin_class = models.ForeignKey(CabinClass, on_delete=models.CASCADE)
    row_number = models.IntegerField()
    seat_letter = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F')])
    occupied = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['flight', 'row_number', 'seat_letter'],
                name='unique_seat_per_flight_cabin_row_letter'
            )
        ]