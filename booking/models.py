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
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, default=None)
    passenger = models.ForeignKey(to=Passenger, on_delete=models.CASCADE)
    confirmation_number = models.CharField(max_length=6, unique=True, db_index=True)
    seat = models.ForeignKey(to=Seat, on_delete=models.CASCADE)
    booking_status = models.ForeignKey(to=BookingStatus, on_delete=models.CASCADE)
