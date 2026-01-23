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