from django.db import models
from django.conf import settings

from user.models import User
from flight.models import Flight
from fare.models import Fare


class Cart(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    departure_flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE, related_name='departure_flight')
    return_flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE, null=True, blank=True, related_name='return_flight')
    departure_fare = models.ForeignKey(to=Fare, on_delete=models.CASCADE, related_name='departure_fare')
    return_fare = models.ForeignKey(to=Fare, on_delete=models.CASCADE, null=True, blank=True, related_name='return_fare')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)