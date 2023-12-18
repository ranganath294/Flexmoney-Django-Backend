from django.contrib.auth.models import BaseUserManager
from .models import *

class MyUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        # creating an instance of any user
        if not email:
            raise ValueError('The given email must be set')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
