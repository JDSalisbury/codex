import random
from dataclasses import dataclass
from typing import Any

from codex.models import Core, CoreBattleInfo, CoreUpgradeInfo, Garage, Move
from codex.constants import CORE_TYPES, RARITIES, CORE_TRACKS, STAT_BOOST_MAP


def track_to_stat_boost(track: str) -> dict[str, int]:
    return STAT_BOOST_MAP.get(track, {})


@dataclass(frozen=True)
class CoreGenRequest:
    name: str
    core_type: str
    rarity: str
    track: str  # Single track choice from TRACKS list
    price: int


def generate_core(garage: Garage, req: CoreGenRequest) -> Core:
    if not garage.has_capacity():
        raise ValueError("Garage has no capacity. Decommission or buy a bay.")

    core = Core.objects.create(
        garage=garage,
        name=req.name,
        type=random.choice(CORE_TYPES),
        rarity=req.rarity,
        lvl=1,
        price=req.price,

    )

    # MVP stats (swap for rarity tables later)
    base_hp = random.randint(90, 130)
    base_physical = random.randint(8, 16)
    base_energy = random.randint(8, 16)
    base_def = random.randint(8, 16)
    base_shield = random.randint(0, 20)
    base_speed = random.randint(6, 14)

    # Apply track boosts to base stats
    boosts = track_to_stat_boost(req.track)
    base_hp += boosts.get("hp", 0)
    base_physical += boosts.get("physical", 0)
    base_energy += boosts.get("energy", 0)
    base_def += boosts.get("defense", 0)
    base_shield += boosts.get("shield", 0)
    base_speed += boosts.get("speed", 0)

    CoreBattleInfo.objects.create(
        core=core,
        hp=base_hp,
        physical=base_physical,
        energy=base_energy,
        defense=base_def,
        shield=base_shield,
        speed=base_speed,
        equip_slots=4,
    )

    CoreUpgradeInfo.objects.create(
        core=core,
        exp=0,
        next_lvl=100,
        upgradeable=True,
        # Store as single-item list for consistency with model
        tracks=[{"name": req.track}],
        lvl_logs=[],
    )

    # Assign starter moves to new core's move pool
    starter_moves = Move.objects.filter(is_starter=True)
    if starter_moves.exists():
        core.moves_pool.set(starter_moves)

    return core
