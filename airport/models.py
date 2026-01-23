from django.db import models

class Airport(models.Model):
    id = models.BigAutoField(primary_key=True)
    airport_code = models.CharField(max_length=3, unique=True, db_index=True)
    airport_name = models.CharField(max_length=50)
    time_zone = models.CharField(max_length=30)