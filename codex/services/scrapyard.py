from codex.models import Core, Scrapyard, Move
from codex.constants import RARITY_PRICES


def decommission_core(core: Core, scrapyard: Scrapyard) -> None:
    if core.decommed:
        return
    core.decommed = True
    core.save(update_fields=["decommed"])

    # snapshot minimal state for MVP
    scrapyard.decommed_cores.append({
        "core_id": str(core.id),
        "name": core.name,
        "rarity": core.rarity,
        "type": core.type,
        "lvl": core.lvl,
    })
    scrapyard.save(update_fields=["decommed_cores"])


def recommission_core(core: Core, operator_bits_cost: int) -> None:
    # MVP: reset to lvl 1, exp 0
    core.decommed = False
    core.lvl = 1
    core.save(update_fields=["decommed", "lvl"])

    if hasattr(core, "upgrade_info"):
        ui = core.upgrade_info
        ui.exp = 0
        ui.next_lvl = 100
        ui.save(update_fields=["exp", "next_lvl"])


def get_move_shop_rotation() -> list:
    """
    Get the current move shop inventory for the Scrapyard.
    MVP: Return all non-starter moves grouped by rarity.
    Future: Implement weekly rotation logic.

    Returns:
        list: List of move dictionaries with id, name, rarity, type, dmg, cost, price
    """
    moves = Move.objects.filter(is_starter=False).order_by('rarity', 'name')

    return [{
        "id": str(move.id),
        "name": move.name,
        "description": move.description,
        "rarity": move.rarity,
        "type": move.type,
        "dmg_type": move.dmg_type,
        "dmg": move.dmg,
        "accuracy": move.accuracy,
        "resource_cost": move.resource_cost,
        "lvl_learned": move.lvl_learned,
        "core_type_identity": move.core_type_identity,
        "price": RARITY_PRICES.get(move.rarity, 100)  # Bits cost to unlock
    } for move in moves]
