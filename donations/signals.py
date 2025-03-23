import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment


@receiver(post_save, sender=Payment)
def generate_confirmation_number(sender, instance, created, **kwargs):
    """
    Generate a random, unique confirmation number using UUID.
    """
    if created and not instance.confirmation_number:
        instance.confirmation_number = uuid.uuid4().hex.upper()
        instance.save()
