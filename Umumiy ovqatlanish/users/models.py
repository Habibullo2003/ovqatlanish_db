from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
