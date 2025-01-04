from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import random
from datetime import date


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('cook', 'Cook'),
        ('waiter', 'Waiter'),
        ('accountant', 'Accountant'),
    ]

    email = models.EmailField(unique=True)
    username = None  # Remove default username
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    restaurant = models.ForeignKey('Restaurant', on_delete=models.SET_NULL, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# Restaurant Model
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    unique_code = models.CharField(max_length=6, unique=True, blank=True)
    subscription_active = models.BooleanField(default=True)
    subscription_date = models.DateField(default=date.today)
    expiration_date = models.DateField(blank=True, null=True)  # Ensure this field exists

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = ''.join(random.choices('0123456789', k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"
