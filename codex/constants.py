# codex/constants.py
# Constants for Core Generation system

RARITY_PRICES = {
    "Common": 100,
    "Uncommon": 250,
    "Rare": 500,
    "Legendary": 1000,
    "Mythic": 2500,
}

RARITIES = ["Common", "Uncommon", "Rare", "Legendary", "Mythic"]

# Core type identities (used for move type restrictions and core generation)
CORE_TYPES = [
    "Techno",
    "Bio",
    "Hybrid",
    "Quantum",
    "Nano",
    "Cyber",
    "Mecha",
    "Plasma",
    "Void",
    "Solar",
    "Arcane",
    "Electric",
    "Magnetic",
    "Gravitic",
    "Thermal",
    "Acidic",
    "Radiant",
    "Psychic",
    "Nuclear",
    "Temporal",
]

CORE_TRACKS = [
    "Balanced",
    "Attack",
    "Defense",
    "Support",
    "Tank",
    "Speed",
]

STAT_BOOST_MAP = {
    "Balanced": {"physical": 5, "energy": 5,
                 "defense": 5, "shield": 5, "speed": 5},
    "Attack": {"physical": 15, "energy": 10},
    "Defense": {"defense": 15, "shield": 10},
    "Support": {"hp": 10, "energy": 10, "speed": 5, "defense": 5},
    "Tank": {"hp": 20, "defense": 10, "shield": 5},
    "Speed": {"speed": 20, "energy": 5},
}

# Move Constants

# Move functions (tactical categories, not type identity restrictions)
# These define the move's role in combat (Attack/Defense/etc)
MOVE_FUNCTIONS = ["Attack", "Defense",
                  "Reaction", "Support", "Stance", "Utility"]

MOVE_DMG_TYPES = ["ENERGY", "PHYSICAL"]

MOVE_TRACK_TYPES = [
    "attack_bias",
    "defense_bias",
    "support_bias",
    "speed_bias",
    "balanced"
]

# Stat ranges for procedural move generation
MOVE_STAT_RANGES = {
    "Common": {
        "dmg": (5, 15),
        "accuracy": (0.75, 0.95),
        "resource_cost": (2, 4)
    },
    "Uncommon": {
        "dmg": (12, 25),
        "accuracy": (0.80, 1.0),
        "resource_cost": (4, 6)
    },
    "Rare": {
        "dmg": (20, 40),
        "accuracy": (0.70, 1.0),
        "resource_cost": (6, 9)
    },
    "Legendary": {
        "dmg": (35, 60),
        "accuracy": (0.65, 1.0),
        "resource_cost": (10, 14)
    },
    "Mythic": {
        "dmg": (50, 100),
        "accuracy": (0.60, 1.0),
        "resource_cost": (14, 20)
    }
}

STARTER_MOVE_NAMES = [
    "Basic Strike",
    "Energy Pulse",
    "Guard Stance",
    "Quick Dodge"
]

# Procedural name generation components
MOVE_ADJECTIVES = [
    "Blazing", "Swift", "Mighty", "Arcane", "Thunder", "Shadow",
    "Crushing", "Piercing", "Frozen", "Molten", "Quantum", "Vicious",
    "Brutal", "Elegant", "Savage", "Refined", "Chaotic", "Divine"
]

MOVE_NOUNS = [
    "Strike", "Blast", "Pulse", "Wave", "Beam", "Lance",
    "Slash", "Crush", "Fury", "Storm", "Barrage", "Cannon",
    "Edge", "Fang", "Claw", "Impact", "Surge", "Flare"
]
