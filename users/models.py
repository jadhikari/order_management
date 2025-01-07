from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.timezone import now
from django.conf import settings
import random


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


# Abstract TimeStamped Model
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created"
    )

    class Meta:
        abstract = True


# Restaurant Model
class Restaurant(TimeStampedModel):
    name = models.CharField(max_length=100)
    unique_code = models.CharField(max_length=6, unique=True, blank=True)
    subscription_active = models.BooleanField(default=True)
    subscription_date = models.DateField(default=now)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = ''.join(random.choices('0123456789', k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Custom User Model
class CustomUser(AbstractUser, TimeStampedModel):
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
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# Profile Model
class RestaurantProfile(models.Model):
    """
    Profile associated with each restaurant.
    """
    restaurant = models.OneToOneField(
        'Restaurant', on_delete=models.CASCADE, related_name='profile'
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.restaurant.name}"
