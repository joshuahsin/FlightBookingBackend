from django.db import models

from booking_status.models import BookingStatus
from flight.models import Flight
from django.conf import settings
from order.models import Order
from passenger.models import Passenger
from seat.models import Seat


# Create your models here.
class Booking(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='bookings')
    flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE)
    passenger = models.ForeignKey(to=Passenger, on_delete=models.CASCADE)
    seat = models.ForeignKey(to=Seat, on_delete=models.CASCADE)
    booking_status = models.ForeignKey(to=BookingStatus, on_delete=models.CASCADE)
    fare_price = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['flight', 'passenger'],
                name='unique_booking_per_flight_passenger'
            )
        ]
