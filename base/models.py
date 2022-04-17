from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password


class AccountManager(BaseUserManager):

    def create_user(self, username=None, password=None, **kwargs):
        account = self.model(username=username)
        account.is_employee = kwargs.get('is_employee', False)
        account.is_restaurant_owner = kwargs.get('is_restaurant_owner', False)
        account.set_password(password)
        account.save()
        return account

    def create_superuser(self, username, password, **kwargs):
        account = self.create_user(username, password, **kwargs)
        account.is_admin = True
        account.save()
        return account


class Account(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True)
    is_employee = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_restaurant_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'

    objects = AccountManager()
