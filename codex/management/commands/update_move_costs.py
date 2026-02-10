"""
Django management command to rescale existing Move resource_cost values
to the new 3d8-balanced cost ranges.

Named moves are mapped to exact new costs.
Procedurally generated moves are linearly interpolated from old range to new range
based on their rarity.

Idempotent — safe to run multiple times.

Usage: python manage.py update_move_costs
"""
from django.core.management.base import BaseCommand
from codex.models import Move


# Exact cost mapping for all named/seeded moves
NAMED_MOVE_COSTS = {
    # Starter (Common)
    "Basic Strike": 3,
    "Energy Pulse": 3,
    "Guard Stance": 2,
    "Quick Dodge": 2,
    # Uncommon
    "Power Strike": 5,
    "Shield Wall": 4,
    "Precision Laser": 4,
    "Tactical Retreat": 4,
    "Nano Repair": 5,
    "Armor Plating": 5,
    # Rare
    "Plasma Cannon": 8,
    "Titanium Slash": 7,
    "Aegis Protocol": 6,
    "Neural Hack": 6,
    "Viral Infection": 7,
    "Regeneration": 7,
    "System Override": 6,
    "Hydraulic Crush": 8,
    # Legendary
    "Quantum Strike": 12,
    "Meteor Hammer": 10,
    "Time Dilation Field": 11,
    "Quantum Disruption": 12,
    "Probability Collapse": 13,
    # Mythic
    "Omega Beam": 17,
    "Apocalypse Fist": 15,
    "Absolute Zero": 18,
}

# Old and new cost ranges per rarity for linear interpolation
OLD_RANGES = {
    "Common": (1, 3),
    "Uncommon": (2, 4),
    "Rare": (3, 6),
    "Legendary": (4, 8),
    "Mythic": (5, 10),
}

NEW_RANGES = {
    "Common": (2, 4),
    "Uncommon": (4, 6),
    "Rare": (6, 9),
    "Legendary": (10, 14),
    "Mythic": (14, 20),
}


def interpolate_cost(old_cost, old_range, new_range):
    """Linearly interpolate a cost from old range to new range."""
    old_min, old_max = old_range
    new_min, new_max = new_range

    if old_max == old_min:
        return new_min

    # Normalize position in old range [0, 1]
    t = (old_cost - old_min) / (old_max - old_min)
    t = max(0.0, min(1.0, t))  # clamp

    # Map to new range
    new_cost = new_min + t * (new_max - new_min)
    return max(1, round(new_cost))


class Command(BaseCommand):
    help = 'Rescale existing Move resource_cost values to new 3d8-balanced ranges'

    def handle(self, *args, **options):
        named_updated = 0
        named_skipped = 0
        procedural_updated = 0
        procedural_skipped = 0

        self.stdout.write(
            self.style.SUCCESS('\n=== Updating Move Costs (3d8 Rebalance) ===\n')
        )

        all_moves = Move.objects.all()
        self.stdout.write(f'Total moves in database: {all_moves.count()}\n')

        for move in all_moves:
            if move.name in NAMED_MOVE_COSTS:
                new_cost = NAMED_MOVE_COSTS[move.name]
                if move.resource_cost == new_cost:
                    named_skipped += 1
                    continue
                old_cost = move.resource_cost
                move.resource_cost = new_cost
                move.save(update_fields=['resource_cost'])
                self.stdout.write(
                    f'  Named: {move.name} [{move.rarity}] '
                    f'{old_cost} -> {new_cost}'
                )
                named_updated += 1
            else:
                # Procedurally generated move — interpolate based on rarity
                rarity = move.rarity
                if rarity not in OLD_RANGES:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ? Unknown rarity "{rarity}" for {move.name}, skipping'
                        )
                    )
                    continue

                new_cost = interpolate_cost(
                    move.resource_cost, OLD_RANGES[rarity], NEW_RANGES[rarity]
                )

                if move.resource_cost == new_cost:
                    procedural_skipped += 1
                    continue

                old_cost = move.resource_cost
                move.resource_cost = new_cost
                move.save(update_fields=['resource_cost'])
                self.stdout.write(
                    f'  Procedural: {move.name} [{rarity}] '
                    f'{old_cost} -> {new_cost}'
                )
                procedural_updated += 1

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\nRebalance Complete!\n'
                f'  Named moves updated: {named_updated}\n'
                f'  Named moves already correct: {named_skipped}\n'
                f'  Procedural moves updated: {procedural_updated}\n'
                f'  Procedural moves already correct: {procedural_skipped}\n'
            )
        )
        self.stdout.write('=' * 60 + '\n')
