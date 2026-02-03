from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+\d{7,15}$',
    message="Phone number must be in E.164 format"
)

# Create your models here.
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[("admin","admin"), ("user","user")])
    phone_number = models.CharField(
        max_length = 16,
        validators = [phone_validator],
        unique=True)
    preferred_contact_method = models.CharField(max_length=20, null=True)


class PendingRegistration(models.Model):
    """Temporary signup data until user verifies email. Deleted after verification."""
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, db_index=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)  # temporary; hashed when User is created
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=16)
    preferred_contact_method = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']