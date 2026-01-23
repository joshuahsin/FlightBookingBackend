# Create your models here.
from django.db import models

from airport.models import Airport


class Flight(models.Model):
    id = models.BigAutoField(primary_key=True)
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name='departing_flight'
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name='arriving_flight'
    )
    departure_date_time = models.DateTimeField()
    arrival_date_time = models.DateTimeField()