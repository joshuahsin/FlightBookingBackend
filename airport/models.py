from django.db import models
from city.models import City

class Airport(models.Model):
    id = models.BigAutoField(primary_key=True)
    airport_code = models.CharField(max_length=3, unique=True, db_index=True)
    airport_name = models.CharField(max_length=50, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='airports')
    #time_zone = models.CharField(max_length=30)