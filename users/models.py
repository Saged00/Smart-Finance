from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, full_name, password=None):
        """
        Creates and saves a User with the given email, full name, and password.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user  = self.model(email=email, full_name=full_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        """
        Creates and saves a superuser with the given email, full name, and password.
        """
        user = self.create_user(email, full_name, password)
        user.is_staff     = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model representing a system user.
    Uses email as the primary login credential and includes fields for 
    full name and administrative status.
    """
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