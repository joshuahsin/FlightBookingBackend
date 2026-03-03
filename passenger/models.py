from django.db import models

# Create your models here.
class Passenger(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'date_of_birth'],
                name='unique_passenger_first_last_dob',
            ),
        ]