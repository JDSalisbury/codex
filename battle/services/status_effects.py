# battle/services/status_effects.py
"""
Status effect engine for the battle system.
Handles applying, ticking, querying, and clearing status effects.

Effects are stored as lists of dicts in BattleCoreState.status_effects (player)
or in the NPC core state dict's 'status_effects' key.
"""
import random


def apply_effect(effects_list: list, effect: dict) -> tuple[list, str]:
    """
    Apply a status effect to a core's effect list.
    Same effect type from same source refreshes duration (no stacking).

    Returns:
        (updated_effects_list, message)
    """
    effect_type = effect['effect_type']

    # Check for existing effect of same type — refresh duration
    for existing in effects_list:
        if existing['effect_type'] == effect_type:
            existing['turns_remaining'] = effect.get('turns_remaining', 0)
            existing['value'] = effect.get('value', 0)
            return effects_list, f"refreshed {effect.get('source_move', effect_type)}"

    effects_list.append(dict(effect))
    return effects_list, f"applied {effect.get('source_move', effect_type)}"


def process_turn_start_effects(effects_list: list, max_hp: int) -> tuple[list, int, list]:
    """
    Process effects at the start of a turn: regen healing, tick durations.

    Returns:
        (updated_effects_list, heal_amount, expired_effect_names)
    """
    heal_amount = 0
    expired = []
    surviving = []

    for effect in effects_list:
        # Regen heals at turn start
        if effect['effect_type'] == 'regen':
            heal_amount += int(max_hp * effect.get('value', 0.10))

        # Tick duration
        turns = effect.get('turns_remaining')
        if turns is not None and turns > 0:
            effect['turns_remaining'] -= 1
            if effect['turns_remaining'] <= 0:
                expired.append(effect.get('source_move', effect['effect_type']))
                continue

        surviving.append(effect)

    return surviving, heal_amount, expired


def get_damage_modifier(defender_effects: list) -> float:
    """
    Calculate a combined damage multiplier from defensive effects.
    Guard (0.5), shield_wall (0.3), aegis (0.5), armor (0.5 to stats — handled separately).
    These stack multiplicatively.
    """
    modifier = 1.0
    for effect in defender_effects:
        etype = effect['effect_type']
        if etype in ('guard', 'shield_wall', 'aegis'):
            modifier *= (1.0 - effect.get('value', 0))
    return modifier


def get_stat_modifier(effects_list: list) -> dict:
    """
    Get stat multipliers from effects like armor.

    Returns:
        dict of stat_name -> multiplier (e.g. {'defense': 1.5, 'shield': 1.5})
    """
    mods = {}
    for effect in effects_list:
        if effect['effect_type'] == 'armor':
            val = effect.get('value', 0.5)
            mods['defense'] = mods.get('defense', 1.0) + val
            mods['shield'] = mods.get('shield', 1.0) + val
    return mods


def get_accuracy_modifier(attacker_effects: list) -> float:
    """
    Get accuracy modifier from debuffs on the attacker.
    accuracy_down reduces accuracy by its value.
    """
    modifier = 1.0
    for effect in attacker_effects:
        if effect['effect_type'] == 'accuracy_down':
            modifier *= (1.0 - effect.get('value', 0))
    return modifier


def check_dodge(defender_effects: list) -> tuple[bool, str | None]:
    """
    Check if defender has an auto-dodge effect (dodge or time_dilation).
    Consumes dodge on use.

    Returns:
        (should_dodge, effect_name_consumed)
    """
    for effect in defender_effects:
        if effect['effect_type'] in ('dodge', 'time_dilation'):
            name = effect.get('source_move', effect['effect_type'])
            # Consume the effect
            effect['turns_remaining'] = 0
            return True, name
    return False, None


def check_stun(effects_list: list) -> bool:
    """Check if the core is stunned and cannot act."""
    return any(e['effect_type'] == 'stun' for e in effects_list)


def check_confusion(effects_list: list) -> bool:
    """
    Check if confusion causes self-hit this turn.
    Returns True if the core hits itself.
    """
    for effect in effects_list:
        if effect['effect_type'] == 'confusion':
            return random.random() < effect.get('value', 0.3)
    return False


def clear_effects(effects_list: list) -> list:
    """Clear all effects (used on switch-out)."""
    return []


def remove_expired(effects_list: list) -> list:
    """Remove effects with 0 turns remaining."""
    return [e for e in effects_list if e.get('turns_remaining', 1) > 0]
