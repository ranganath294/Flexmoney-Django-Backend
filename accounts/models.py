from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import MyUserManager
from django.conf import settings
from django.utils import timezone
import datetime



class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    name = models.CharField(max_length=255)
    dob = models.DateField()
    mobile = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Email_verification(models.Model):
    email = models.EmailField(verbose_name="email", max_length=255, unique=True)
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def otp_is_valid(self, minutes=10):
        """
        Check if the OTP is still valid.
        Returns True if the OTP is less than `minutes` old, False otherwise.
        """
        time_diff = timezone.now() - self.created_at
        return time_diff.total_seconds() < minutes * 60