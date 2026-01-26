from django.db import models

# Create your models here.
class City(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=30, db_index=True)
    country = models.CharField(max_length=30)
    time_zone = models.CharField(max_length=30)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'country'],
                name='unique_city_country'
            )
        ]