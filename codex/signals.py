from django.db.models.signals import post_save
from django.dispatch import receiver

from codex.models import Operator
from codex.services.operator_init import initialize_operator


@receiver(post_save, sender=Operator)
def initialize_new_operator(sender, instance, created, **kwargs):
    """
    Signal handler to initialize new operators with:
    - Default Garage (3 bay capacity)
    - Starter Core (Common rarity)
    - Starting resources (500 bits)

    Only fires on creation (created=True).
    Idempotent: won't duplicate if Garage already exists.
    """
    if created:
        initialize_operator(instance)
