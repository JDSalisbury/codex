"""
Move Factory Service
Handles move creation (curated and procedural) and core-move management.
"""
import random
from dataclasses import dataclass
from typing import Optional
from codex.models import Move, Core, CoreEquippedMove, ImageAsset
from codex.constants import (
    MOVE_STAT_RANGES,
    MOVE_FUNCTIONS,
    MOVE_DMG_TYPES,
    MOVE_ADJECTIVES,
    MOVE_NOUNS,
    CORE_TYPES
)


@dataclass(frozen=True)
class MoveCreateRequest:
    """Request object for creating a curated move template"""
    name: str
    description: str
    type: str  # Attack/Defense/Reaction/Support/Stance/Utility
    dmg_type: str  # ENERGY or PHYSICAL
    dmg: int
    accuracy: float
    resource_cost: int
    rarity: str
    lvl_learned: int = 0
    core_type_identity: str = ""
    track_type: str = ""
    image_id: Optional[str] = None
    is_starter: bool = False


@dataclass(frozen=True)
class MoveEquipRequest:
    """Request object for equipping a move to a core"""
    core_id: str
    move_id: str
    slot: int


def create_move(req: MoveCreateRequest) -> Move:
    """
    Create a new move template with exact stats (curated mode).
    Used by: admin, seed data, frontend move creation

    Raises:
        ValueError: If validation fails (invalid function, dmg_type, type_identity, accuracy, duplicate name)
    """
    # Validate move function
    if req.type not in MOVE_FUNCTIONS:
        raise ValueError(
            f"Invalid move function '{req.type}'. Must be one of: {MOVE_FUNCTIONS}"
        )

    # Validate damage type
    if req.dmg_type not in MOVE_DMG_TYPES:
        raise ValueError(f"Invalid dmg_type: {req.dmg_type}. Must be ENERGY or PHYSICAL")

    # Validate type identity (if provided)
    if req.core_type_identity and req.core_type_identity not in CORE_TYPES:
        raise ValueError(
            f"Invalid core_type_identity '{req.core_type_identity}'. "
            f"Must be one of: {CORE_TYPES} or empty for Generic moves"
        )

    if not 0.0 <= req.accuracy <= 1.0:
        raise ValueError(f"Accuracy must be 0.0-1.0, got {req.accuracy}")

    # Check for duplicate names
    if Move.objects.filter(name=req.name).exists():
        raise ValueError(f"Move '{req.name}' already exists")

    # Get image if provided
    image = None
    if req.image_id:
        try:
            image = ImageAsset.objects.get(source_id=req.image_id)
        except ImageAsset.DoesNotExist:
            pass  # Allow null images

    # Create move
    move = Move.objects.create(
        name=req.name,
        description=req.description,
        type=req.type,
        dmg_type=req.dmg_type,
        dmg=req.dmg,
        accuracy=req.accuracy,
        resource_cost=req.resource_cost,
        rarity=req.rarity,
        lvl_learned=req.lvl_learned,
        core_type_identity=req.core_type_identity,
        track_type=req.track_type,
        image=image,
        is_starter=req.is_starter
    )

    return move


def generate_random_move(rarity: str, move_type: str, dmg_type: str) -> Move:
    """
    Generate a procedural move with random stats within rarity ranges.
    Used by: rewards, loot drops, procedural content

    Args:
        rarity: Common, Uncommon, Rare, Legendary, or Mythic
        move_type: Attack, Defense, Reaction, Support, Stance, or Utility
        dmg_type: ENERGY or PHYSICAL

    Returns:
        Move: Newly created random move

    Raises:
        ValueError: If invalid parameters
    """
    # Validation
    if rarity not in MOVE_STAT_RANGES:
        raise ValueError(f"Invalid rarity: {rarity}")

    if move_type not in MOVE_FUNCTIONS:
        raise ValueError(f"Invalid move_type: {move_type}")

    if dmg_type not in MOVE_DMG_TYPES:
        raise ValueError(f"Invalid dmg_type: {dmg_type}")

    # Get stat ranges for this rarity
    ranges = MOVE_STAT_RANGES[rarity]

    # Generate random stats
    dmg = random.randint(*ranges["dmg"])
    accuracy = round(random.uniform(*ranges["accuracy"]), 2)
    resource_cost = random.randint(*ranges["resource_cost"])

    # Generate unique name
    base_name = f"{random.choice(MOVE_ADJECTIVES)} {random.choice(MOVE_NOUNS)}"
    name = base_name
    counter = 1

    while Move.objects.filter(name=name).exists():
        name = f"{base_name} {counter}"
        counter += 1

    # Generate description
    description = f"A {rarity.lower()} {move_type.lower()} move that deals {dmg_type.lower()} damage."

    # Create the move
    move = Move.objects.create(
        name=name,
        description=description,
        type=move_type,
        dmg_type=dmg_type,
        dmg=dmg,
        accuracy=accuracy,
        resource_cost=resource_cost,
        rarity=rarity,
        lvl_learned=0,
        is_starter=False
    )

    return move


def equip_move_to_core(req: MoveEquipRequest) -> CoreEquippedMove:
    """
    Equip a move from garage library OR core's exclusive pool to a specific slot.

    Validates:
    - Core and move exist
    - Slot is valid (1..equip_slots)
    - Move is in garage library OR core's move_pool
    - Sufficient copies available (for garage library moves)
    - Slot is not already occupied
    - Type identity matches

    Args:
        req: MoveEquipRequest with core_id, move_id, slot

    Returns:
        CoreEquippedMove: The created equipped move instance

    Raises:
        ValueError: If validation fails
    """
    from codex.models import GarageMoveLibrary

    # Get core and move
    try:
        core = Core.objects.select_related('garage', 'battle_info').get(id=req.core_id)
        move = Move.objects.get(id=req.move_id)
    except Core.DoesNotExist:
        raise ValueError(f"Core with ID {req.core_id} not found")
    except Move.DoesNotExist:
        raise ValueError(f"Move with ID {req.move_id} not found")

    # Validate slot range
    max_slots = core.battle_info.equip_slots if core.battle_info else 4
    if not 1 <= req.slot <= max_slots:
        raise ValueError(f"Slot must be 1-{max_slots}, got {req.slot}")

    # Check if move is available from EITHER source
    in_core_pool = core.moves_pool.filter(id=move.id).exists()
    in_garage_library = GarageMoveLibrary.objects.filter(
        garage=core.garage,
        move=move
    ).exists()

    if not (in_core_pool or in_garage_library):
        raise ValueError(
            f"{move.name} not available. Must be in garage library or core's exclusive moves."
        )

    # If from garage library (not core-exclusive), check if copies available
    if in_garage_library and not in_core_pool:
        library_entry = GarageMoveLibrary.objects.get(garage=core.garage, move=move)

        # Count how many cores currently have this equipped
        equipped_count = CoreEquippedMove.objects.filter(
            core__garage=core.garage,
            move=move
        ).count()

        if equipped_count >= library_entry.copies_owned:
            raise ValueError(
                f"All copies of {move.name} are currently equipped. "
                f"(Owned: {library_entry.copies_owned}, Equipped: {equipped_count})"
            )

    # Check if slot is occupied
    if CoreEquippedMove.objects.filter(core=core, slot=req.slot).exists():
        raise ValueError(f"Slot {req.slot} already occupied. Unequip the existing move first.")

    # Check if move is already equipped (database constraint will also catch this)
    if CoreEquippedMove.objects.filter(core=core, move=move).exists():
        raise ValueError(f"Move '{move.name}' is already equipped to {core.name} in another slot")

    # Validate type identity restrictions
    if move.core_type_identity:  # Non-empty = type-restricted move
        if move.core_type_identity != core.type:
            raise ValueError(
                f"Type identity mismatch: {move.name} requires a {move.core_type_identity} "
                f"Core, but {core.name} is {core.type}. Only Generic moves (empty type_identity) "
                f"or matching type moves can be equipped."
            )
    # Empty core_type_identity = Generic move, any core can equip

    # Create equipped move (database constraints prevent duplicates)
    try:
        equipped = CoreEquippedMove.objects.create(
            core=core,
            move=move,
            slot=req.slot
        )
    except Exception as e:
        raise ValueError(f"Failed to equip move: {str(e)}")

    return equipped


def unequip_move_from_core(core_id: str, slot: int) -> None:
    """
    Remove a move from a core's equipped slot.
    The move remains in the core's move_pool and can be re-equipped.

    Args:
        core_id: UUID of the core
        slot: Slot number to unequip

    Raises:
        ValueError: If core not found or slot is empty
    """
    try:
        core = Core.objects.get(id=core_id)
    except Core.DoesNotExist:
        raise ValueError(f"Core with ID {core_id} not found")

    try:
        equipped = CoreEquippedMove.objects.get(core=core, slot=slot)
        equipped.delete()
    except CoreEquippedMove.DoesNotExist:
        raise ValueError(f"No move equipped in slot {slot}")


def add_move_to_pool(core_id: str, move_id: str) -> None:
    """
    Add a move to a core's available move pool (learn/unlock).
    Used when: leveling up, shop purchase, quest reward.

    Args:
        core_id: UUID of the core
        move_id: UUID of the move to add

    Raises:
        ValueError: If core or move not found
    """
    try:
        core = Core.objects.get(id=core_id)
        move = Move.objects.get(id=move_id)
    except Core.DoesNotExist:
        raise ValueError(f"Core with ID {core_id} not found")
    except Move.DoesNotExist:
        raise ValueError(f"Move with ID {move_id} not found")

    # Add to pool (M2M handles duplicates gracefully)
    core.moves_pool.add(move)


# ==================== GARAGE MOVE LIBRARY ====================

def add_move_to_garage_library(garage_id: str, move_id: str):
    """
    Add a purchased move to the garage's shared library.
    Increments copies_owned if already present (max 2).
    """
    from codex.models import Garage, Move, GarageMoveLibrary

    garage = Garage.objects.get(id=garage_id)
    move = Move.objects.get(id=move_id)

    # Check if move is a starter (cannot be purchased)
    if move.is_starter:
        raise ValueError("Starter moves cannot be added to garage library")

    # Check if signature move (cannot be purchased)
    if move.is_signature:
        raise ValueError("Signature moves cannot be added to garage library")

    # Get or create library entry
    library_entry, created = GarageMoveLibrary.objects.get_or_create(
        garage=garage,
        move=move,
        defaults={'copies_owned': 1}
    )

    if not created:
        # Already own this move, check if can buy another copy
        if library_entry.copies_owned >= 2:
            raise ValueError(
                f"Maximum copies (2) of {move.name} already owned. "
                f"Cannot purchase more."
            )
        library_entry.copies_owned += 1
        library_entry.save()

    return library_entry


def remove_move_from_garage_library(garage_id: str, move_id: str) -> None:
    """
    Remove a move from garage library (decrement copy count).
    Used for: refunds, selling moves back (future feature).
    """
    from codex.models import Garage, Move, GarageMoveLibrary

    garage = Garage.objects.get(id=garage_id)
    move = Move.objects.get(id=move_id)

    try:
        library_entry = GarageMoveLibrary.objects.get(garage=garage, move=move)
    except GarageMoveLibrary.DoesNotExist:
        raise ValueError(f"{move.name} not found in garage library")

    if library_entry.copies_owned > 1:
        library_entry.copies_owned -= 1
        library_entry.save()
    else:
        # Last copy - delete the entry
        library_entry.delete()


def get_garage_available_moves(garage_id: str, core_id: str = None) -> list:
    """
    Get all moves available to equip for cores in this garage.
    Combines:
    - Garage shared library (purchased moves)
    - Core-exclusive moves (if core_id provided: starters, signatures)

    Returns list of Move objects with availability status.
    """
    from codex.models import Garage, Core, Move, GarageMoveLibrary, CoreEquippedMove

    garage = Garage.objects.get(id=garage_id)

    # Get shared library moves
    library_moves = Move.objects.filter(
        garagemovelibrary__garage=garage
    ).distinct()

    available_moves = []

    # Add library moves with copy tracking
    for move in library_moves:
        library_entry = GarageMoveLibrary.objects.get(garage=garage, move=move)

        # Count how many cores currently have this equipped
        equipped_count = CoreEquippedMove.objects.filter(
            core__garage=garage,
            move=move
        ).count()

        copies_available = library_entry.copies_owned - equipped_count
        if copies_available > 0:
            available_moves.append({
                'move': move,
                'source': 'garage_library',
                'copies_owned': library_entry.copies_owned,
                'copies_equipped': equipped_count,
                'copies_available': copies_available,
                'can_equip': True
            })

    # If specific core provided, add core-exclusive moves
    if core_id:
        core = Core.objects.get(id=core_id)
        exclusive_moves = core.moves_pool.exclude(
            id__in=library_moves.values_list('id', flat=True)
        )

        for move in exclusive_moves:
            is_equipped = CoreEquippedMove.objects.filter(
                core=core,
                move=move
            ).exists()

            if not is_equipped:
                available_moves.append({
                    'move': move,
                    'source': 'core_exclusive',
                    'is_starter': move.is_starter,
                    'is_signature': move.is_signature,
                    'is_equipped': False,
                    'can_equip': True
                })

    return available_moves
