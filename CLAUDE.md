# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CoDEX is a turn-based Core battler game where players (Operators) manage rosters of modular Cores (combat frames). Battles are 1v1 with 3 Cores per side, using card-like moves fueled by shared team resources generated through d8 rolls each turn.

This is a Django REST Framework backend implementing the core game systems: Operator progression, Core generation/management, Garage capacity mechanics, Scrapyard decommissioning/recommissioning, and the move deck system.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (already exists in .venv)
source .venv/bin/activate

# Install dependencies (if needed)
pip install django djangorestframework
```

### Database
```bash
# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Create superuser for admin access
python manage.py createsuperuser
```

### Running the Server
```bash
# Run development server
python manage.py runserver

# Access admin interface at http://localhost:8000/admin/
```

### Django Shell
```bash
# Access Django shell for testing models and services
python manage.py shell
```

## Architecture

### Core Game Loop
The game follows a cycle: Acquire Cores (Cyber Codex) → Build Teams (Garage) → Battle → Earn Rewards → Upgrade/Refine → Decommission old Cores (Scrapyard).

### Data Model Relationships

**Operator** (1) ←→ (1) **Garage** ←→ (many) **Core**
- Operator is the persistent player identity with level, currency (bits/premium), wins/losses
- Garage has limited capacity (bay_doors) and stores team loadouts
- Cores belong to a Garage and can be decommissioned (soft delete)

**Core** relationships:
- Core (1) ←→ (1) CoreBattleInfo: combat stats (HP, physical, energy, defense, shield, speed)
- Core (1) ←→ (1) CoreUpgradeInfo: progression data (exp, tracks, level logs)
- Core (many) ←→ (many) Move via CoreEquippedMove: slot-based equipped moves
- Core (many) ←→ (many) Move via moves_pool: available moves the Core can learn

**Move System**:
- Moves have damage types (Energy/Physical), resource costs, accuracy, and type identity restrictions
- CoreEquippedMove is the through-table enforcing slot uniqueness and preventing duplicate moves per Core
- Moves reference ImageAssets for visual representation

**Supporting Models**:
- **Equipment**: items with bonuses, can represent moves (is_move=True)
- **ImageAsset**: reusable art with RGB palette variants and animation references
- **Scrapyard**: global system storing decommissioned core snapshots and shop rotation data

### Service Layer (codex/services/)

The service layer contains game logic separate from Django models:

- **core_factory.py**: `generate_core(garage, CoreGenRequest)` - handles Core creation with stat generation, capacity checking, and related model initialization (CoreBattleInfo, CoreUpgradeInfo)
- **scrapyard.py**: `decommission_core()` and `recommission_core()` - manages Core lifecycle and Scrapyard snapshots

### Key Constraints

1. **Garage Capacity**: Cores cannot be created if `garage.has_capacity()` returns False. Check active (non-decommissioned) core count vs bay_doors.
2. **Move Slots**: CoreEquippedMove enforces unique slots per Core and prevents duplicate move assignments via database constraints.
3. **Type Identity**: Moves have core_type_identity restrictions (similar to MTG Commander color identity). Enforcement logic not yet implemented but field exists.

## Design Patterns

- **Service Functions**: Use service layer functions for complex operations involving multiple models
- **TimestampedModel**: Abstract base class provides created_at/updated_at to all models
- **UUID Primary Keys**: All main models use UUIDs for distributed-safe IDs
- **JSONField Flexibility**: Several fields (tracks, loadouts, zones, choices) use JSON for MVP flexibility before formalizing into separate models
- **Soft Deletes**: Cores use `decommed` flag rather than deletion, preserving data for Scrapyard recommissioning

## Game Mechanics Reference

### Resource System
- Two shared team pools: Energy Ammo and Physical Ammo
- Each turn: each Core rolls d8, player assigns result to either pool
- Moves cost resources from these pools

### Rarity System
Rarities: Common, Uncommon, Rare, Legendary, Mythic
- Higher rarities have better stat ranges and growth curves
- Mythic/Legendary are named templates (not fully random)

### Track System
Cores have "tracks" that define their identity and growth patterns:
- Damage Track: Energy vs Physical bias
- Fortitude Track: fast/weak vs slow/strong archetypes
- Growth Track: early vs late scaling
Stored in CoreUpgradeInfo.tracks as JSON until formalized.

### Move Card Types
Referenced in Move.type field: Attack, Defense, Reaction, Support, Stance, Utility
- Reactions can trigger during opponent's turn (timing logic not yet implemented)
