from django.db import models
from django.contrib.auth.models import AbstractUser


class Permission(models.Model):
    name = models.CharField(max_length=200)


class Role(models.Model):
    name = models.CharField(max_length=200)
    permissions = models.ManyToManyField(Permission)


class Users(AbstractUser):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)

    # real password will be hashed, so i need a long column for the result.
    password = models.CharField(max_length=200)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    # set default field to None, in order to log in with password instead of username.
    # specify what will be used instead of the default username.
    username = None
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []
