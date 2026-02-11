"""
Django management command to seed the database with curated moves.
Usage: python manage.py seed_moves
"""
from django.core.management.base import BaseCommand
from codex.services.move_factory import create_move, MoveCreateRequest
from codex.models import Move


class Command(BaseCommand):
    help = 'Seed the database with starter and curated moves'

    def handle(self, *args, **options):
        moves_to_create = [
            # ===== STARTER MOVES (Common rarity, is_starter=True, Generic - any Core can use) =====
            MoveCreateRequest(
                name="Basic Strike",
                description="A standard physical attack with reliable damage. Every Core starts with this fundamental technique.",
                type="Attack",
                dmg_type="PHYSICAL",
                dmg=18,
                accuracy=0.90,
                resource_cost=3,
                rarity="Common",
                lvl_learned=0,
                core_type_identity="",  # Generic - any Core can equip
                track_type="balanced",
                is_starter=True
            ),
            MoveCreateRequest(
                name="Energy Pulse",
                description="Channel raw energy into a focused blast. A staple energy attack for all Cores.",
                type="Attack",
                dmg_type="ENERGY",
                dmg=20,
                accuracy=0.85,
                resource_cost=3,
                rarity="Common",
                lvl_learned=0,
                core_type_identity="",  # Generic - any Core can equip
                track_type="attack_bias",
                is_starter=True
            ),
            MoveCreateRequest(
                name="Guard Stance",
                description="Adopt a defensive posture, reducing incoming damage. A fundamental defensive technique.",
                type="Defense",
                dmg_type="PHYSICAL",
                dmg=0,
                accuracy=1.0,
                resource_cost=2,
                rarity="Common",
                lvl_learned=0,
                core_type_identity="",  # Generic - any Core can equip
                track_type="defense_bias",
                is_starter=True
            ),
            MoveCreateRequest(
                name="Quick Dodge",
                description="Evade the next attack with precise timing. Speed is your greatest defense.",
                type="Reaction",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=1.0,
                resource_cost=2,
                rarity="Common",
                lvl_learned=0,
                core_type_identity="",  # Generic - any Core can equip
                track_type="speed_bias",
                is_starter=True
            ),

            # ===== UNCOMMON MOVES (lvl 3+) =====
            MoveCreateRequest(
                name="Power Strike",
                description="A devastating blow that sacrifices accuracy for raw damage. High risk, high reward.",
                type="Attack",
                dmg_type="PHYSICAL",
                dmg=22,
                accuracy=0.75,
                resource_cost=5,
                rarity="Uncommon",
                lvl_learned=3,
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Shield Wall",
                description="Project an energy barrier that absorbs incoming damage for your team.",
                type="Defense",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=1.0,
                resource_cost=4,
                rarity="Uncommon",
                lvl_learned=3,
                track_type="defense_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Precision Laser",
                description="A concentrated beam of energy with pinpoint accuracy.",
                type="Attack",
                dmg_type="ENERGY",
                dmg=18,
                accuracy=0.95,
                resource_cost=4,
                rarity="Uncommon",
                lvl_learned=3,
                track_type="balanced",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Tactical Retreat",
                description="Fall back and prepare a counterattack. Sometimes the best offense is knowing when to regroup.",
                type="Support",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=1.0,
                resource_cost=4,
                rarity="Uncommon",
                lvl_learned=3,
                track_type="support_bias",
                is_starter=False
            ),

            # ===== RARE MOVES (lvl 5+) =====
            MoveCreateRequest(
                name="Plasma Cannon",
                description="Superheated plasma tears through shields and armor alike. Devastating but energy-intensive.",
                type="Attack",
                dmg_type="ENERGY",
                dmg=35,
                accuracy=0.80,
                resource_cost=8,
                rarity="Rare",
                lvl_learned=5,
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Titanium Slash",
                description="A blade technique reinforced with advanced metallurgy. Cuts through any defense.",
                type="Attack",
                dmg_type="PHYSICAL",
                dmg=38,
                accuracy=0.85,
                resource_cost=7,
                rarity="Rare",
                lvl_learned=5,
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Aegis Protocol",
                description="Activate emergency defensive systems. Drastically reduces damage for a short duration.",
                type="Stance",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=1.0,
                resource_cost=6,
                rarity="Rare",
                lvl_learned=5,
                track_type="defense_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Neural Hack",
                description="Disrupt enemy targeting systems, causing their next attack to miss.",
                type="Utility",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=0.75,
                resource_cost=6,
                rarity="Rare",
                lvl_learned=5,
                track_type="support_bias",
                is_starter=False
            ),

            # ===== LEGENDARY MOVES (lvl 8+) =====
            MoveCreateRequest(
                name="Quantum Strike",
                description="Phase through defenses to deal guaranteed damage. Manipulates probability itself.",
                type="Attack",
                dmg_type="ENERGY",
                dmg=50,
                accuracy=1.0,
                resource_cost=12,
                rarity="Legendary",
                lvl_learned=8,
                track_type="balanced",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Meteor Hammer",
                description="Channel gravitational force into a single crushing blow. Nothing survives direct impact.",
                type="Attack",
                dmg_type="PHYSICAL",
                dmg=55,
                accuracy=0.70,
                resource_cost=10,
                rarity="Legendary",
                lvl_learned=8,
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Time Dilation Field",
                description="Slow down local time, making all attacks against you miss. Reality bends at your command.",
                type="Reaction",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=1.0,
                resource_cost=11,
                rarity="Legendary",
                lvl_learned=8,
                track_type="defense_bias",
                is_starter=False
            ),

            # ===== MYTHIC MOVES (lvl 10+) =====
            MoveCreateRequest(
                name="Omega Beam",
                description="The ultimate energy weapon. Channels the Core's full power into a devastating beam.",
                type="Attack",
                dmg_type="ENERGY",
                dmg=85,
                accuracy=0.90,
                resource_cost=17,
                rarity="Mythic",
                lvl_learned=10,
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Apocalypse Fist",
                description="A legendary physical technique passed down through generations of Cores. Each strike reshapes the battlefield.",
                type="Attack",
                dmg_type="PHYSICAL",
                dmg=90,
                accuracy=0.85,
                resource_cost=15,
                rarity="Mythic",
                lvl_learned=10,
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Absolute Zero",
                description="Freeze all enemy systems to absolute zero. Nothing can move, nothing can attack.",
                type="Stance",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=0.60,
                resource_cost=18,
                rarity="Mythic",
                lvl_learned=10,
                track_type="support_bias",
                is_starter=False
            ),

            # ===== TYPE-RESTRICTED MOVES (Demonstrate type identity system) =====
            # Techno-specific moves
            MoveCreateRequest(
                name="Quantum Disruption",
                description="A devastating energy attack that exploits quantum instabilities. Techno Cores only.",
                type="Attack",
                dmg_type="ENERGY",
                dmg=55,
                accuracy=0.85,
                resource_cost=12,
                rarity="Legendary",
                lvl_learned=8,
                core_type_identity="Techno",  # Type-restricted
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Nano Repair",
                description="Deploy microscopic repair bots to restore systems. Techno Cores' signature heal.",
                type="Support",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=1.0,
                resource_cost=5,
                rarity="Uncommon",
                lvl_learned=3,
                core_type_identity="Techno",  # Type-restricted
                track_type="support_bias",
                is_starter=False
            ),

            # Bio-specific moves
            MoveCreateRequest(
                name="Viral Infection",
                description="Inject a biological agent that deals damage over time. Bio Cores' specialty.",
                type="Attack",
                dmg_type="PHYSICAL",
                dmg=30,
                accuracy=0.90,
                resource_cost=7,
                rarity="Rare",
                lvl_learned=5,
                core_type_identity="Bio",  # Type-restricted
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Regeneration",
                description="Organic healing factor restores health rapidly. Bio Cores' natural ability.",
                type="Stance",
                dmg_type="PHYSICAL",
                dmg=0,
                accuracy=1.0,
                resource_cost=7,
                rarity="Rare",
                lvl_learned=5,
                core_type_identity="Bio",  # Type-restricted
                track_type="defense_bias",
                is_starter=False
            ),

            # Cyber-specific moves
            MoveCreateRequest(
                name="System Override",
                description="Hack enemy targeting systems to redirect their attacks. Cyber Cores excel at this.",
                type="Utility",
                dmg_type="ENERGY",
                dmg=0,
                accuracy=0.80,
                resource_cost=6,
                rarity="Rare",
                lvl_learned=5,
                core_type_identity="Cyber",  # Type-restricted
                track_type="support_bias",
                is_starter=False
            ),

            # Quantum-specific moves
            MoveCreateRequest(
                name="Probability Collapse",
                description="Manipulate quantum states to guarantee a critical hit. Quantum Cores' ace.",
                type="Attack",
                dmg_type="ENERGY",
                dmg=60,
                accuracy=1.0,
                resource_cost=13,
                rarity="Legendary",
                lvl_learned=8,
                core_type_identity="Quantum",  # Type-restricted
                track_type="balanced",
                is_starter=False
            ),

            # Mecha-specific moves
            MoveCreateRequest(
                name="Hydraulic Crush",
                description="Mechanical pistons deliver crushing force. Mecha Cores' brutal attack.",
                type="Attack",
                dmg_type="PHYSICAL",
                dmg=45,
                accuracy=0.75,
                resource_cost=8,
                rarity="Rare",
                lvl_learned=5,
                core_type_identity="Mecha",  # Type-restricted
                track_type="attack_bias",
                is_starter=False
            ),
            MoveCreateRequest(
                name="Armor Plating",
                description="Deploy reinforced plating to reduce all incoming damage. Mecha durability at its finest.",
                type="Stance",
                dmg_type="PHYSICAL",
                dmg=0,
                accuracy=1.0,
                resource_cost=5,
                rarity="Uncommon",
                lvl_learned=3,
                core_type_identity="Mecha",  # Type-restricted
                track_type="defense_bias",
                is_starter=False
            ),
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(
            self.style.SUCCESS('\n=== Starting Move Seeding ===\n')
        )

        for move_req in moves_to_create:
            existing = Move.objects.filter(name=move_req.name).first()
            if existing:
                # Update existing move stats to match seed data
                changed = False
                field_map = {
                    'dmg': 'dmg', 'accuracy': 'accuracy',
                    'resource_cost': 'resource_cost', 'type': 'type',
                    'dmg_type': 'dmg_type', 'rarity': 'rarity',
                    'lvl_learned': 'lvl_learned',
                }
                for req_field, model_field in field_map.items():
                    new_val = getattr(move_req, req_field)
                    if getattr(existing, model_field) != new_val:
                        setattr(existing, model_field, new_val)
                        changed = True
                if changed:
                    existing.save()
                    self.stdout.write(
                        self.style.WARNING(f'~ Updated existing move: {move_req.name}')
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'- Skipping unchanged move: {move_req.name}')
                    )
                    skipped_count += 1
                continue

            try:
                move = create_move(move_req)
                rarity_display = f"[{move.rarity}]".ljust(12)
                starter_mark = "★ STARTER" if move.is_starter else ""
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created {rarity_display} {move.name} {starter_mark}'
                    )
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to create {move_req.name}: {e}')
                )

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Seeding Complete!\n'
                f'  Created: {created_count} moves\n'
                f'  Updated: {updated_count} moves\n'
                f'  Skipped: {skipped_count} unchanged moves\n'
                f'  Total in database: {Move.objects.count()} moves\n'
            )
        )
        self.stdout.write('=' * 60 + '\n')
