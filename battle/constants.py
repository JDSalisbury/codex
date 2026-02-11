# battle/constants.py
# Constants for the Battle system

# Battle Types
BATTLE_TYPE_PVP = "PVP"
BATTLE_TYPE_PVE = "PVE"
BATTLE_TYPE_MISSION = "MISSION"

BATTLE_TYPES = [BATTLE_TYPE_PVP, BATTLE_TYPE_PVE, BATTLE_TYPE_MISSION]

# Battle Status
BATTLE_STATUS_PENDING = "PENDING"
BATTLE_STATUS_ACTIVE = "ACTIVE"
BATTLE_STATUS_COMPLETED = "COMPLETED"
BATTLE_STATUS_ABANDONED = "ABANDONED"

BATTLE_STATUSES = [
    BATTLE_STATUS_PENDING,
    BATTLE_STATUS_ACTIVE,
    BATTLE_STATUS_COMPLETED,
    BATTLE_STATUS_ABANDONED,
]

# Action Types
ACTION_TYPE_MOVE = "MOVE"
ACTION_TYPE_SWITCH = "SWITCH"
ACTION_TYPE_PASS = "PASS"
ACTION_TYPE_GAIN_RESOURCE = "GAIN_RESOURCE"
ACTION_TYPE_REACTION = "REACTION"

ACTION_TYPES = [
    ACTION_TYPE_MOVE,
    ACTION_TYPE_SWITCH,
    ACTION_TYPE_PASS,
    ACTION_TYPE_GAIN_RESOURCE,
    ACTION_TYPE_REACTION,
]

# Resource Pool Types
RESOURCE_ENERGY = "ENERGY"
RESOURCE_PHYSICAL = "PHYSICAL"

RESOURCE_TYPES = [RESOURCE_ENERGY, RESOURCE_PHYSICAL]

# Dice Configuration
DICE_MIN = 1
DICE_MAX = 8
DICE_TYPE = "d8"

# Team Configuration
MAX_CORES_PER_TEAM = 3
CORE_POSITIONS = [0, 1, 2]

# Mission Difficulty
DIFFICULTY_EASY = "EASY"
DIFFICULTY_MEDIUM = "MEDIUM"
DIFFICULTY_HARD = "HARD"
DIFFICULTY_EXTREME = "EXTREME"

DIFFICULTIES = [
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
    DIFFICULTY_EXTREME,
]

# Difficulty multipliers for enemy stat scaling
DIFFICULTY_MULTIPLIERS = {
    DIFFICULTY_EASY: 0.8,
    DIFFICULTY_MEDIUM: 1.0,
    DIFFICULTY_HARD: 1.3,
    DIFFICULTY_EXTREME: 1.6,
}

# Base rewards per difficulty
DIFFICULTY_REWARDS = {
    DIFFICULTY_EASY: {"bits": 50, "exp": 25},
    DIFFICULTY_MEDIUM: {"bits": 100, "exp": 50},
    DIFFICULTY_HARD: {"bits": 200, "exp": 100},
    DIFFICULTY_EXTREME: {"bits": 400, "exp": 200},
}

# Mission Status
MISSION_STATUS_AVAILABLE = "AVAILABLE"
MISSION_STATUS_ACTIVE = "ACTIVE"
MISSION_STATUS_COMPLETED = "COMPLETED"
MISSION_STATUS_FAILED = "FAILED"
MISSION_STATUS_EXPIRED = "EXPIRED"

MISSION_STATUSES = [
    MISSION_STATUS_AVAILABLE,
    MISSION_STATUS_ACTIVE,
    MISSION_STATUS_COMPLETED,
    MISSION_STATUS_FAILED,
    MISSION_STATUS_EXPIRED,
]

# Mail Types
MAIL_TYPE_SYSTEM = "SYSTEM"
MAIL_TYPE_REWARD = "REWARD"
MAIL_TYPE_BATTLE_RESULT = "BATTLE_RESULT"
MAIL_TYPE_MISSION_UPDATE = "MISSION_UPDATE"

MAIL_TYPES = [
    MAIL_TYPE_SYSTEM,
    MAIL_TYPE_REWARD,
    MAIL_TYPE_BATTLE_RESULT,
    MAIL_TYPE_MISSION_UPDATE,
]

# Combat Constants
CRITICAL_HIT_MULTIPLIER = 1.5
BASE_CRITICAL_CHANCE = 0.0625  # 6.25% — matches Pokémon Gen VI+
MAX_ACCURACY = 1.0
MIN_DAMAGE = 1  # Minimum damage dealt (prevents 0 damage)
STAB_MULTIPLIER = 1.25  # Same-Type Attack Bonus when Core type matches move type identity

# Damage Formula Constants (Pokémon-inspired)
DAMAGE_STAT_SMOOTHING = 15      # added to atk and def to compress stat ratios toward 1.0
DAMAGE_DIVISOR = 3              # calibrated for CoDEX stat ranges (Pokémon uses 50)
DAMAGE_FLAT_BONUS = 2           # minimum damage floor on hit
DAMAGE_VARIANCE_MIN = 0.85      # random roll lower bound
DAMAGE_VARIANCE_MAX = 1.0       # random roll upper bound (Pokémon: 85-100%)

# 3d8 Resource Economy Reference
# Each alive Core rolls 1d8 per turn; player allocates each roll to Energy or Physical pool.
# Pools accumulate across turns. Move costs are balanced against these income rates.
THREE_D8_MIN = 3
THREE_D8_MAX = 24
THREE_D8_MEAN = 13.5
THREE_D8_PERCENTILES = {10: 7, 25: 10, 50: 13, 75: 17, 90: 19, 95: 21}
EXPECTED_INCOME_PER_POOL = {3: 6.75, 2: 4.5, 1: 2.25}  # cores alive → avg per resource action

# ──────────────────────────────────────────────
# Status Effect Definitions
# ──────────────────────────────────────────────
# Maps move name -> effect definition applied when the move is used.
# "target": "self" applies to the user, "enemy" applies to the opponent.
# "apply_chance": probability the effect lands (1.0 = guaranteed).
# "turns_remaining": how many turns it lasts (None = instant).
MOVE_EFFECT_MAP = {
    "Guard Stance": {
        "effect_type": "guard",
        "target": "self",
        "turns_remaining": 1,
        "value": 0.5,
        "apply_chance": 1.0,
        "message": "raised its guard!",
    },
    "Quick Dodge": {
        "effect_type": "dodge",
        "target": "self",
        "turns_remaining": 1,
        "value": 1.0,
        "apply_chance": 1.0,
        "message": "is ready to evade!",
    },
    "Shield Wall": {
        "effect_type": "shield_wall",
        "target": "self",
        "turns_remaining": 2,
        "value": 0.3,
        "apply_chance": 1.0,
        "message": "projected a shield wall!",
    },
    "Tactical Retreat": {
        "effect_type": "tactical_retreat",
        "target": "self",
        "turns_remaining": None,
        "value": 0.25,
        "apply_chance": 1.0,
        "message": "is preparing a tactical retreat!",
    },
    "Aegis Protocol": {
        "effect_type": "aegis",
        "target": "self",
        "turns_remaining": 2,
        "value": 0.5,
        "apply_chance": 1.0,
        "message": "activated Aegis Protocol!",
    },
    "Neural Hack": {
        "effect_type": "accuracy_down",
        "target": "enemy",
        "turns_remaining": 2,
        "value": 0.3,
        "apply_chance": 0.75,
        "message": "disrupted enemy targeting systems!",
    },
    "Time Dilation Field": {
        "effect_type": "time_dilation",
        "target": "self",
        "turns_remaining": 1,
        "value": 1.0,
        "apply_chance": 1.0,
        "message": "warped local time!",
    },
    "Absolute Zero": {
        "effect_type": "stun",
        "target": "enemy",
        "turns_remaining": 1,
        "value": 1.0,
        "apply_chance": 0.60,
        "message": "froze all enemy systems!",
    },
    "Nano Repair": {
        "effect_type": "heal",
        "target": "self",
        "turns_remaining": None,
        "value": 0.25,
        "apply_chance": 1.0,
        "message": "deployed repair nanobots!",
    },
    "Regeneration": {
        "effect_type": "regen",
        "target": "self",
        "turns_remaining": 3,
        "value": 0.10,
        "apply_chance": 1.0,
        "message": "activated regeneration!",
    },
    "Armor Plating": {
        "effect_type": "armor",
        "target": "self",
        "turns_remaining": 2,
        "value": 0.5,
        "apply_chance": 1.0,
        "message": "deployed reinforced plating!",
    },
    "System Override": {
        "effect_type": "confusion",
        "target": "enemy",
        "turns_remaining": 2,
        "value": 0.3,
        "apply_chance": 0.80,
        "message": "hacked enemy targeting!",
    },
}

# Effect types that are considered defensive buffs
DEFENSIVE_EFFECTS = {'guard', 'shield_wall', 'aegis', 'armor', 'dodge', 'time_dilation'}

# Effect types that are debuffs on the enemy
DEBUFF_EFFECTS = {'accuracy_down', 'stun', 'confusion'}
