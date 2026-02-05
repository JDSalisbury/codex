# battle/services/npc_ai.py
"""
NPC AI decision making for PvE battles.
MVP: Simple random selection with resource checking.
"""
import random
from typing import Optional

from battle.models import Battle


def choose_npc_action(battle: Battle) -> dict:
    """
    Choose an action for the NPC.

    Returns:
        {
            'action_type': 'move'|'switch'|'pass',
            'move': {...} if action_type == 'move',
            'new_core_index': int if action_type == 'switch',
        }
    """
    npc_team = battle.rewards.get('npc_team', {})
    active_idx = npc_team.get('active_core_index', 0)
    cores = npc_team.get('cores', [])

    if not cores:
        return {'action_type': 'pass'}

    active_core = cores[active_idx] if active_idx < len(cores) else None

    # Check if active core is KO'd - must switch
    if active_core and active_core.get('is_knocked_out'):
        switch_target = find_alive_core(cores, exclude_idx=active_idx)
        if switch_target is not None:
            return {
                'action_type': 'switch',
                'new_core_index': switch_target,
            }
        else:
            return {'action_type': 'pass'}  # All cores KO'd

    # Get available moves (ones we can afford)
    available_moves = get_affordable_moves(active_core, npc_team)

    if available_moves:
        # Random move selection (MVP AI)
        chosen_move = random.choice(available_moves)
        return {
            'action_type': 'move',
            'move': chosen_move,
        }
    else:
        # No affordable moves - pass
        return {'action_type': 'pass'}


def get_affordable_moves(core: dict, team_state: dict) -> list[dict]:
    """
    Get list of moves the core can afford to use.
    """
    if not core:
        return []

    energy_pool = team_state.get('energy_pool', 0)
    physical_pool = team_state.get('physical_pool', 0)

    affordable = []
    for move in core.get('equipped_moves', []):
        cost = move.get('resource_cost', 0)
        dmg_type = move.get('dmg_type', 'PHYSICAL')

        if dmg_type == 'ENERGY' and energy_pool >= cost:
            affordable.append(move)
        elif dmg_type == 'PHYSICAL' and physical_pool >= cost:
            affordable.append(move)

    return affordable


def find_alive_core(cores: list[dict], exclude_idx: Optional[int] = None) -> Optional[int]:
    """
    Find the index of an alive core to switch to.
    """
    for i, core in enumerate(cores):
        if i != exclude_idx and not core.get('is_knocked_out'):
            return i
    return None


def allocate_npc_dice(battle: Battle, dice_rolls: list[dict]) -> list[dict]:
    """
    Automatically allocate NPC dice to pools.
    MVP strategy: 50/50 split, higher rolls to energy.
    """
    if not dice_rolls:
        return []

    # Sort rolls by value (highest first)
    sorted_rolls = sorted(dice_rolls, key=lambda x: x['roll_value'], reverse=True)

    allocations = []
    for i, roll in enumerate(sorted_rolls):
        # Alternate between energy and physical, with bias toward energy for higher rolls
        if i % 2 == 0:
            pool = 'energy'
        else:
            pool = 'physical'

        allocations.append({
            'core_id': roll['core_id'],
            'pool': pool,
        })
        roll['allocated_to'] = pool

    return allocations
