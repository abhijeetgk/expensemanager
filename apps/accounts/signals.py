"""
Signal handlers for the accounts app.

Demonstrates the Observer pattern using Django signals.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a user is saved.
    
    Args:
        sender: The model class
        instance: The actual instance being saved
        created: Boolean; True if a new record was created
        **kwargs: Additional keyword arguments
    """
    if created:
        # Perform actions after user creation
        # For example: send welcome email, create user profile, etc.
        pass

