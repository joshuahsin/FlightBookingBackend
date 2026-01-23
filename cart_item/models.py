from django.db import models

from cart.models import Cart
from fare.models import Fare
from flight.models import Flight


# Create your models here.
class CartItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE)
    flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE)
    fare = models.ForeignKey(to=Fare, on_delete=models.CASCADE)