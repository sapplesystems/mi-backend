from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user_role = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = "mi_users"
