from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Restaurant, RestaurantProfile


@receiver(post_save, sender=Restaurant)
def create_restaurant_profile(sender, instance, created, **kwargs):
    """
    Automatically create a RestaurantProfile when a new Restaurant is created.
    """
    if created:
        RestaurantProfile.objects.get_or_create(restaurant=instance)
