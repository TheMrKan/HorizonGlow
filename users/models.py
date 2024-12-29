from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.hashers import make_password


class User(AbstractUser):
    REQUIRED_FIELDS = [*AbstractUser.REQUIRED_FIELDS, "secret_phrase"]

    secret_phrase = models.CharField("Secret phrase", max_length=128)
    balance = models.DecimalField("Balance", max_digits=10, decimal_places=2, default=0)
    is_seller = models.BooleanField("Seller status", default=False)