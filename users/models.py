from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    # Custom manager using email
    def create_user(self, email, full_name, password=None):
        # Create normal user
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user  = self.model(email=email, full_name=full_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        # Create admin user
        user = self.create_user(email, full_name, password)
        user.is_staff     = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Custom User model
    email        = models.EmailField(unique=True)
    full_name    = models.CharField(max_length=150)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    member_since = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']
    objects = UserManager()

    def __str__(self):
        return self.email