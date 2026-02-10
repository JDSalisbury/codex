# battle/services/battle_engine.py
"""
Core battle logic service. Server-authoritative battle engine.
"""
import random
from typing import Optional
from django.db import transaction

from battle.models import (
    Battle, BattleTeam, BattleCoreState, BattleTurn, BattleAction, DiceRoll,
    NPCOperator, NPCCore
)
from codex.models import Operator, Core


def create_battle_from_npc(operator_id: str, npc_id: str) -> Battle:
    """
    Initialize a new Battle between a player and an NPC.
    Creates Battle, BattleTeams, and BattleCoreStates for both sides.
    """
    operator = Operator.objects.get(id=operator_id)
    npc = NPCOperator.objects.prefetch_related(
        'cores', 'cores__equipped_moves', 'cores__equipped_moves__move'
    ).get(id=npc_id)

    with transaction.atomic():
        # Create the battle
        battle = Battle.objects.create(
            operator_1=operator,
            battle_type="PVE",
            status="ACTIVE",
            current_turn=0
        )

        # Create player team
        player_team = BattleTeam.objects.create(
            battle=battle,
            operator=operator,
            energy_pool=0,
            physical_pool=0,
            active_core_index=0
        )

        # Get player's cores from their garage loadout
        garage = operator.garage
        player_cores = list(
            Core.objects.filter(garage=garage, decommed=False)
            .select_related('battle_info')
            .prefetch_related('equipped_moves', 'coreequippedmove_set__move')
            .order_by('created_at')[:3]
        )

        # Create battle states for player cores
        for i, core in enumerate(player_cores):
            battle_info = core.battle_info
            BattleCoreState.objects.create(
                team=player_team,
                core=core,
                position=i,
                current_hp=battle_info.hp,
                max_hp=battle_info.hp,
                is_knocked_out=False
            )

        # Create NPC team (using operator record for consistency, even though NPC)
        # For NPCs, we create a pseudo-team. They don't have a real Operator.
        # We'll store the NPC reference differently - using the battle's operator_2=None
        # and tracking NPC ID in battle metadata

        # Create a simple team for NPC - we need to handle this specially
        # For now, we'll create NPC core states without a real Core model reference
        npc_team = create_npc_battle_team(battle, npc)

        return battle


def create_npc_battle_team(battle: Battle, npc: NPCOperator) -> BattleTeam:
    """
    Create a battle team for an NPC opponent.
    NPC cores are stored as NPCCore, not real Core objects.
    We'll store their data directly in BattleCoreState.
    """
    # For NPC teams, we need a placeholder operator or handle differently
    # Since Battle requires an operator, we'll use a special approach:
    # Store NPC data in the battle's rewards JSON field for now
    battle.rewards['npc_id'] = str(npc.id)
    battle.rewards['npc_name'] = npc.call_sign
    battle.save(update_fields=['rewards'])

    # For NPC team, we still need a BattleTeam but with special handling
    # Create a "virtual" team entry - we'll need to query NPCCores separately
    # Actually, looking at the model, BattleTeam requires an operator FK.
    # Let's store NPC battle state in the battle's rewards field as JSON instead

    npc_cores = list(npc.cores.prefetch_related('equipped_moves__move').order_by('team_position'))

    # Store NPC team state in battle rewards
    npc_team_state = {
        'energy_pool': 0,
        'physical_pool': 0,
        'active_core_index': 0,
        'cores': []
    }

    for core in npc_cores:
        core_state = {
            'id': str(core.id),
            'name': core.name,
            'core_type': core.core_type,
            'rarity': core.rarity,
            'lvl': core.lvl,
            'image_url': core.image_url,
            'position': core.team_position,
            'current_hp': core.hp,
            'max_hp': core.hp,
            'is_knocked_out': False,
            'stats': {
                'hp': core.hp,
                'physical': core.physical,
                'energy': core.energy,
                'defense': core.defense,
                'shield': core.shield,
                'speed': core.speed,
            },
            'equipped_moves': [
                {
                    'id': str(em.move.id),
                    'name': em.move.name,
                    'slot': em.slot,
                    'dmg_type': em.move.dmg_type,
                    'dmg': em.move.dmg,
                    'accuracy': em.move.accuracy,
                    'resource_cost': em.move.resource_cost,
                    'type': em.move.type,
                }
                for em in core.equipped_moves.all()
            ]
        }
        npc_team_state['cores'].append(core_state)

    battle.rewards['npc_team'] = npc_team_state
    battle.save(update_fields=['rewards'])

    return None  # No actual BattleTeam record for NPC


def validate_action(battle: Battle, team_side: str, action_type: str, action_data: dict) -> tuple[bool, str]:
    """
    Validate a player action before execution.

    Args:
        battle: The current battle
        team_side: 'player' or 'npc'
        action_type: 'move', 'switch', 'pass', or 'gain_resource'
        action_data: Additional data (move_id, new_core_index, etc.)

    Returns:
        (is_valid, error_message)
    """
    if team_side == 'player':
        team = battle.teams.first()
        if not team:
            return False, "Player team not found"

        active_core_state = team.core_states.filter(position=team.active_core_index).first()
        if not active_core_state:
            return False, "Active core not found"

        if active_core_state.is_knocked_out:
            if action_type != 'switch':
                return False, "Active core is knocked out - must switch"
    else:
        # NPC validation happens in npc_ai
        pass

    if action_type == 'gain_resource':
        return True, ""

    if action_type == 'move':
        move_id = action_data.get('move_id')
        if not move_id:
            return False, "No move specified"

        if team_side == 'player':
            # Check if the move is equipped
            core = active_core_state.core
            equipped = core.coreequippedmove_set.filter(move_id=move_id).first()
            if not equipped:
                return False, "Move not equipped on active core"

            move = equipped.move

            # Check resource cost
            if move.dmg_type == 'ENERGY':
                if team.energy_pool < move.resource_cost:
                    return False, f"Not enough energy ({team.energy_pool}/{move.resource_cost})"
            else:  # PHYSICAL
                if team.physical_pool < move.resource_cost:
                    return False, f"Not enough physical ammo ({team.physical_pool}/{move.resource_cost})"

    elif action_type == 'switch':
        new_index = action_data.get('new_core_index')
        if new_index is None:
            return False, "No core index specified for switch"

        if team_side == 'player':
            if new_index < 0 or new_index > 2:
                return False, "Invalid core index"

            target_state = team.core_states.filter(position=new_index).first()
            if not target_state:
                return False, "Target core not found"

            if target_state.is_knocked_out:
                return False, "Cannot switch to knocked out core"

            if new_index == team.active_core_index:
                return False, "Already active core"

    return True, ""


def execute_move(battle: Battle, team_side: str, move_data: dict) -> dict:
    """
    Execute a move action. Returns result data.
    """
    result = {
        'action_type': 'move',
        'success': False,
        'damage_dealt': 0,
        'was_critical': False,
        'accuracy_check': False,
        'move_name': '',
        'source_core': '',
        'target_core': '',
    }

    if team_side == 'player':
        player_team = battle.teams.first()
        active_state = player_team.core_states.filter(position=player_team.active_core_index).first()
        core = active_state.core

        equipped = core.coreequippedmove_set.filter(move_id=move_data['move_id']).first()
        move = equipped.move

        # Deduct resource cost
        if move.dmg_type == 'ENERGY':
            player_team.energy_pool -= move.resource_cost
        else:
            player_team.physical_pool -= move.resource_cost
        player_team.save()

        # Get attacker stats
        attacker_stats = core.battle_info

        # Get NPC target
        npc_team = battle.rewards.get('npc_team', {})
        npc_active_idx = npc_team.get('active_core_index', 0)
        npc_cores = npc_team.get('cores', [])
        target_core = npc_cores[npc_active_idx] if npc_cores else None

        if target_core and not target_core.get('is_knocked_out'):
            # Calculate damage
            damage = calculate_damage(
                attacker_stats={'physical': attacker_stats.physical, 'energy': attacker_stats.energy},
                defender_stats=target_core['stats'],
                move={'dmg': move.dmg, 'dmg_type': move.dmg_type, 'accuracy': move.accuracy},
                attacker_level=core.lvl
            )

            # Apply damage
            target_core['current_hp'] = max(0, target_core['current_hp'] - damage['damage'])
            if target_core['current_hp'] <= 0:
                target_core['is_knocked_out'] = True

            # Save NPC state back
            battle.rewards['npc_team'] = npc_team
            battle.save(update_fields=['rewards'])

            result.update({
                'success': True,
                'damage_dealt': damage['damage'],
                'was_critical': damage['critical'],
                'accuracy_check': damage['hit'],
                'move_name': move.name,
                'source_core': core.name,
                'target_core': target_core['name'],
            })
    else:
        # NPC attacking player
        npc_team = battle.rewards.get('npc_team', {})
        npc_active_idx = npc_team.get('active_core_index', 0)
        npc_cores = npc_team.get('cores', [])
        attacker = npc_cores[npc_active_idx] if npc_cores else None

        if not attacker:
            return result

        move = move_data.get('move')
        if not move:
            return result

        # Deduct NPC resources
        if move['dmg_type'] == 'ENERGY':
            npc_team['energy_pool'] = max(0, npc_team.get('energy_pool', 0) - move['resource_cost'])
        else:
            npc_team['physical_pool'] = max(0, npc_team.get('physical_pool', 0) - move['resource_cost'])

        # Get player target
        player_team = battle.teams.first()
        target_state = player_team.core_states.filter(position=player_team.active_core_index).first()

        if target_state and not target_state.is_knocked_out:
            damage = calculate_damage(
                attacker_stats=attacker['stats'],
                defender_stats={
                    'defense': target_state.core.battle_info.defense,
                    'shield': target_state.core.battle_info.shield,
                },
                move=move,
                attacker_level=attacker.get('lvl', 5)
            )

            target_state.current_hp = max(0, target_state.current_hp - damage['damage'])
            if target_state.current_hp <= 0:
                target_state.is_knocked_out = True
            target_state.save()

            result.update({
                'success': True,
                'damage_dealt': damage['damage'],
                'was_critical': damage['critical'],
                'accuracy_check': damage['hit'],
                'move_name': move['name'],
                'source_core': attacker['name'],
                'target_core': target_state.core.name,
            })

        battle.rewards['npc_team'] = npc_team
        battle.save(update_fields=['rewards'])

    return result


def execute_switch(battle: Battle, team_side: str, new_index: int) -> dict:
    """
    Execute a switch action.
    """
    result = {
        'action_type': 'switch',
        'success': False,
        'new_active_core': '',
        'old_active_core': '',
    }

    if team_side == 'player':
        team = battle.teams.first()
        old_state = team.core_states.filter(position=team.active_core_index).first()
        new_state = team.core_states.filter(position=new_index).first()

        if new_state and not new_state.is_knocked_out:
            team.active_core_index = new_index
            team.save()

            result.update({
                'success': True,
                'new_active_core': new_state.core.name,
                'old_active_core': old_state.core.name if old_state else '',
            })
    else:
        npc_team = battle.rewards.get('npc_team', {})
        npc_cores = npc_team.get('cores', [])
        old_idx = npc_team.get('active_core_index', 0)

        if 0 <= new_index < len(npc_cores):
            target = npc_cores[new_index]
            if not target.get('is_knocked_out'):
                npc_team['active_core_index'] = new_index
                battle.rewards['npc_team'] = npc_team
                battle.save(update_fields=['rewards'])

                result.update({
                    'success': True,
                    'new_active_core': target['name'],
                    'old_active_core': npc_cores[old_idx]['name'] if old_idx < len(npc_cores) else '',
                })

    return result


def execute_gain_resource(battle: Battle, team_side: str) -> dict:
    """
    Execute a gain_resource action for a team.
    Rolls dice for the team. For NPC, auto-allocates immediately.
    For player, returns rolls (client handles allocation separately).

    Returns:
        Result dict with action_type, success, rolls, and pools (if NPC).
    """
    from battle.services import npc_ai

    rolls = roll_dice_for_team(battle, team_side)

    result = {
        'action_type': 'gain_resource',
        'success': True,
        'rolls': rolls,
    }

    if team_side == 'npc':
        # NPC auto-allocates immediately
        npc_allocations = npc_ai.allocate_npc_dice(battle, rolls)
        pools = allocate_dice(battle, 'npc', npc_allocations)
        result['pools'] = pools

    return result


def calculate_damage(attacker_stats: dict, defender_stats: dict, move: dict, attacker_level: int = 5) -> dict:
    """
    Calculate damage using Pokémon-inspired Gen V+ formula adapted for CoDEX stat ranges.

    Formula:
        level_factor = (2 * level / 5) + 2
        stat_ratio = (attack + 5) / (defense + 5)
        damage = (level_factor * base_damage * stat_ratio) / 3 + 2
        damage *= uniform(0.85, 1.0)
        crit: 6.25% chance, 1.5x
    """
    from battle.constants import (
        DAMAGE_STAT_SMOOTHING, DAMAGE_DIVISOR, DAMAGE_FLAT_BONUS,
        DAMAGE_VARIANCE_MIN, DAMAGE_VARIANCE_MAX,
        BASE_CRITICAL_CHANCE, CRITICAL_HIT_MULTIPLIER, MIN_DAMAGE,
    )

    base_damage = move.get('dmg', 0)
    dmg_type = move.get('dmg_type', 'PHYSICAL')
    accuracy = move.get('accuracy', 1.0)

    # Accuracy check
    hit = random.random() <= accuracy
    if not hit:
        return {'damage': 0, 'critical': False, 'hit': False}

    # Get relevant stats
    if dmg_type == 'ENERGY':
        attack = attacker_stats.get('energy', 10)
        defense = defender_stats.get('shield', 10)
    else:
        attack = attacker_stats.get('physical', 10)
        defense = defender_stats.get('defense', 10)

    # Prevent division by zero
    defense = max(1, defense)

    # Pokémon-inspired damage formula
    level_factor = (2 * attacker_level / 5) + 2
    stat_ratio = (attack + DAMAGE_STAT_SMOOTHING) / (defense + DAMAGE_STAT_SMOOTHING)
    damage = (level_factor * base_damage * stat_ratio) / DAMAGE_DIVISOR + DAMAGE_FLAT_BONUS

    # Random variance (85-100%, matching Pokémon)
    variance = random.uniform(DAMAGE_VARIANCE_MIN, DAMAGE_VARIANCE_MAX)
    damage *= variance

    # Critical hit check (6.25% chance, 1.5x damage)
    critical = random.random() < BASE_CRITICAL_CHANCE
    if critical:
        damage *= CRITICAL_HIT_MULTIPLIER

    # Round to integer
    damage = max(MIN_DAMAGE, int(damage))

    return {'damage': damage, 'critical': critical, 'hit': True}


def check_team_defeated(battle: Battle, team_side: str) -> bool:
    """
    Check if all cores on a team are knocked out.
    """
    if team_side == 'player':
        team = battle.teams.first()
        if not team:
            return True
        return all(
            state.is_knocked_out
            for state in team.core_states.all()
        )
    else:
        npc_team = battle.rewards.get('npc_team', {})
        npc_cores = npc_team.get('cores', [])
        return all(core.get('is_knocked_out', False) for core in npc_cores)


def serialize_battle_state(battle: Battle) -> dict:
    """
    Serialize the full battle state for frontend consumption.
    """
    player_team = battle.teams.first()
    npc_team = battle.rewards.get('npc_team', {})

    player_data = None
    if player_team:
        player_cores = []
        for state in player_team.core_states.select_related('core', 'core__battle_info').prefetch_related('core__coreequippedmove_set__move').order_by('position'):
            core = state.core
            player_cores.append({
                'id': str(core.id),
                'name': core.name,
                'type': core.type,
                'rarity': core.rarity,
                'lvl': core.lvl,
                'image_url': core.image_url,
                'position': state.position,
                'current_hp': state.current_hp,
                'max_hp': state.max_hp,
                'is_knocked_out': state.is_knocked_out,
                'stats': {
                    'hp': core.battle_info.hp,
                    'physical': core.battle_info.physical,
                    'energy': core.battle_info.energy,
                    'defense': core.battle_info.defense,
                    'shield': core.battle_info.shield,
                    'speed': core.battle_info.speed,
                },
                'equipped_moves': [
                    {
                        'id': str(em.move.id),
                        'name': em.move.name,
                        'slot': em.slot,
                        'dmg_type': em.move.dmg_type,
                        'dmg': em.move.dmg,
                        'accuracy': em.move.accuracy,
                        'resource_cost': em.move.resource_cost,
                        'type': em.move.type,
                    }
                    for em in core.coreequippedmove_set.all()
                ]
            })

        player_data = {
            'energy_pool': player_team.energy_pool,
            'physical_pool': player_team.physical_pool,
            'active_core_index': player_team.active_core_index,
            'cores': player_cores,
        }

    return {
        'battle_id': str(battle.id),
        'status': battle.status,
        'current_turn': battle.current_turn,
        'player_team': player_data,
        'enemy_team': npc_team,
        'npc_id': battle.rewards.get('npc_id'),
        'npc_name': battle.rewards.get('npc_name'),
    }


def roll_dice_for_team(battle: Battle, team_side: str) -> list[dict]:
    """
    Roll d8 for each non-KO'd core on a team.
    Returns list of dice roll data.
    """
    rolls = []

    if team_side == 'player':
        team = battle.teams.first()
        for state in team.core_states.filter(is_knocked_out=False):
            roll_value = random.randint(1, 8)
            state.last_dice_roll = roll_value
            state.save(update_fields=['last_dice_roll'])
            rolls.append({
                'core_id': str(state.core.id),
                'core_name': state.core.name,
                'roll_value': roll_value,
                'allocated_to': None,
            })
    else:
        npc_team = battle.rewards.get('npc_team', {})
        for core in npc_team.get('cores', []):
            if not core.get('is_knocked_out'):
                roll_value = random.randint(1, 8)
                core['last_dice_roll'] = roll_value
                rolls.append({
                    'core_id': core['id'],
                    'core_name': core['name'],
                    'roll_value': roll_value,
                    'allocated_to': None,
                })
        battle.rewards['npc_team'] = npc_team
        battle.save(update_fields=['rewards'])

    return rolls


def allocate_dice(battle: Battle, team_side: str, allocations: list[dict]) -> dict:
    """
    Allocate dice rolls to energy or physical pools.

    Args:
        allocations: [{'core_id': str, 'pool': 'energy'|'physical'}, ...]

    Returns:
        Updated pool totals
    """
    if team_side == 'player':
        team = battle.teams.first()

        for alloc in allocations:
            state = team.core_states.filter(core_id=alloc['core_id']).first()
            if state and state.last_dice_roll:
                if alloc['pool'] == 'energy':
                    team.energy_pool += state.last_dice_roll
                else:
                    team.physical_pool += state.last_dice_roll

        team.save()
        return {
            'energy_pool': team.energy_pool,
            'physical_pool': team.physical_pool,
        }
    else:
        npc_team = battle.rewards.get('npc_team', {})

        for alloc in allocations:
            for core in npc_team.get('cores', []):
                if core['id'] == alloc['core_id'] and core.get('last_dice_roll'):
                    if alloc['pool'] == 'energy':
                        npc_team['energy_pool'] = npc_team.get('energy_pool', 0) + core['last_dice_roll']
                    else:
                        npc_team['physical_pool'] = npc_team.get('physical_pool', 0) + core['last_dice_roll']

        battle.rewards['npc_team'] = npc_team
        battle.save(update_fields=['rewards'])

        return {
            'energy_pool': npc_team.get('energy_pool', 0),
            'physical_pool': npc_team.get('physical_pool', 0),
        }


def end_battle(battle: Battle, winner_side: str) -> dict:
    """
    Finalize the battle and return rewards.
    """
    battle.status = 'COMPLETED'

    npc_id = battle.rewards.get('npc_id')
    result = {
        'winner': winner_side,
        'rewards': {},
    }

    if winner_side == 'player':
        # Player won - award rewards
        if npc_id:
            try:
                npc = NPCOperator.objects.get(id=npc_id)
                result['rewards'] = {
                    'bits': npc.reward_bits,
                    'exp': npc.reward_exp,
                }
                battle.winner = battle.operator_1
            except NPCOperator.DoesNotExist:
                pass

    battle.save()
    return result
