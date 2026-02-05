from django.db import transaction

from codex.models import Operator, Garage
from codex.services.core_factory import generate_core, CoreGenRequest


STARTER_BITS = 500
STARTER_CORE_NAME = "Mk-I Frame"
STARTER_CORE_TYPE = "Balanced"
STARTER_CORE_RARITY = "Common"


@transaction.atomic
def initialize_operator(operator: Operator) -> None:
    """
    Initialize a new operator with starting resources, garage, and starter core.

    Idempotent: Safe to call multiple times (checks for existing Garage).

    Args:
        operator: The Operator instance to initialize

    Raises:
        ValueError: If core generation fails
    """
    # Idempotency check: If garage already exists, skip initialization
    if hasattr(operator, 'garage'):
        return

    # Set starting bits
    operator.bits = STARTER_BITS
    operator.save(update_fields=['bits'])

    # Create Garage with default 3-bay capacity
    garage = Garage.objects.create(
        operator=operator,
        bay_doors=3,
        core_loadouts=[]
    )

    # Generate starter core
    starter_request = CoreGenRequest(
        name=STARTER_CORE_NAME,
        core_type=STARTER_CORE_TYPE,
        rarity=STARTER_CORE_RARITY,
        track="Balanced",  # Balanced track for starter core
        price=0     # Free starter core
    )

    try:
        generate_core(garage, starter_request)
    except ValueError as e:
        raise ValueError(f"Failed to create starter core for operator {operator.id}: {e}")
