# battle/management/commands/seed_arena_npcs.py
"""
Management command to seed E-rank Arena NPCs.
Creates 8 NPC Operators with 3 cores each and equipped moves.

Usage: python manage.py seed_arena_npcs
"""
from django.core.management.base import BaseCommand
from battle.models import NPCOperator, NPCCore, NPCCoreEquippedMove
from codex.models import Move


class Command(BaseCommand):
    help = 'Seeds E-rank Arena NPCs with cores and moves'

    def handle(self, *args, **options):
        # Check if NPCs already exist
        if NPCOperator.objects.filter(arena_rank='E').exists():
            self.stdout.write(self.style.WARNING(
                'E-rank NPCs already exist. Delete them first to reseed.'
            ))
            return

        # Get available moves (use simpler ones for E-rank)
        moves = {m.name: m for m in Move.objects.all()}

        basic_physical = [
            moves.get('Basic Strike'),
            moves.get('Power Strike'),
            moves.get('Titanium Slash'),
            moves.get('Hydraulic Crush'),
        ]
        basic_energy = [
            moves.get('Energy Pulse'),
            moves.get('Precision Laser'),
            moves.get('Plasma Cannon'),
        ]
        defensive = [
            moves.get('Guard Stance'),
            moves.get('Shield Wall'),
            moves.get('Armor Plating'),
        ]
        support = [
            moves.get('Tactical Retreat'),
            moves.get('Nano Repair'),
        ]

        # Filter out None values
        basic_physical = [m for m in basic_physical if m]
        basic_energy = [m for m in basic_energy if m]
        defensive = [m for m in defensive if m]
        support = [m for m in support if m]

        # NPC Data - Floor numbering: #1 = gate boss (top), #8 = weakest (starting point)
        # Players start at highest floor number and work their way to #1
        npcs_data = [
            {
                'call_sign': 'RUST',
                'title': 'Junkyard Dog',
                'floor': 8,  # Starting opponent
                'difficulty_rating': 1,
                'is_gate_boss': False,
                'unlocks_rank': '',
                'bio': "Salvaged from the scrapheaps of Sector 7, RUST pilots a cobbled-together rig that's more rust than metal. Don't let the rough exterior fool you—there's cunning beneath that corroded frame.",
                'reward_bits': 50,
                'reward_exp': 25,
                'win_mail_subject': 'You Got Lucky',
                'win_mail_body': "Tch. My rig was acting up today. Next time won't be so easy, newbie. -RUST",
                'lose_mail_subject': 'As Expected',
                'lose_mail_body': "Hah! Come back when you've got some real iron under your feet. -RUST",
                'cores': [
                    {'name': 'Scrap-1', 'type': 'SALVAGE', 'rarity': 'Common', 'lvl': 1, 'hp': 85, 'physical': 12, 'energy': 6, 'defense': 8, 'shield': 4, 'speed': 8},
                    {'name': 'Junk-2', 'type': 'SALVAGE', 'rarity': 'Common', 'lvl': 1, 'hp': 75, 'physical': 8, 'energy': 10, 'defense': 6, 'shield': 8, 'speed': 10},
                    {'name': 'Heap-3', 'type': 'SALVAGE', 'rarity': 'Common', 'lvl': 2, 'hp': 90, 'physical': 10, 'energy': 8, 'defense': 10, 'shield': 6, 'speed': 6},
                ],
            },
            {
                'call_sign': 'SOCKET',
                'title': 'The Wire',
                'floor': 7,
                'difficulty_rating': 2,
                'is_gate_boss': False,
                'unlocks_rank': '',
                'bio': "A former maintenance technician who turned their repair expertise into combat prowess. SOCKET's cores are always running at optimal efficiency.",
                'reward_bits': 75,
                'reward_exp': 35,
                'win_mail_subject': 'Diagnostic Report',
                'win_mail_body': "ANALYSIS: Your combat efficiency exceeded expectations by 12%. RECOMMENDATION: Continue current training regimen. -SOCKET",
                'lose_mail_subject': 'System Error',
                'lose_mail_body': "ERROR 404: Victory not found. SUGGESTION: Recalibrate combat algorithms. -SOCKET",
                'cores': [
                    {'name': 'Conductor-A', 'type': 'TECH', 'rarity': 'Common', 'lvl': 2, 'hp': 80, 'physical': 8, 'energy': 14, 'defense': 6, 'shield': 10, 'speed': 12},
                    {'name': 'Capacitor-B', 'type': 'TECH', 'rarity': 'Common', 'lvl': 2, 'hp': 85, 'physical': 10, 'energy': 12, 'defense': 8, 'shield': 8, 'speed': 10},
                    {'name': 'Resistor-C', 'type': 'TECH', 'rarity': 'Common', 'lvl': 1, 'hp': 95, 'physical': 6, 'energy': 8, 'defense': 12, 'shield': 12, 'speed': 6},
                ],
            },
            {
                'call_sign': 'GRINDER',
                'title': 'Metal Teeth',
                'floor': 6,
                'difficulty_rating': 2,
                'is_gate_boss': False,
                'unlocks_rank': '',
                'bio': "GRINDER earned their name in the underground fight circuits, where their brutal close-combat style turned opponents into scrap. They fight dirty and they fight mean.",
                'reward_bits': 75,
                'reward_exp': 35,
                'win_mail_subject': 'ROUND 2?',
                'win_mail_body': "THAT WAS FUN. LET'S GO AGAIN SOMETIME. -GRINDER",
                'lose_mail_subject': 'CHEWED UP',
                'lose_mail_body': "ANOTHER ONE FOR THE SCRAP PILE. BETTER LUCK NEXT TIME. -GRINDER",
                'cores': [
                    {'name': 'Masher', 'type': 'BRAWLER', 'rarity': 'Common', 'lvl': 2, 'hp': 100, 'physical': 14, 'energy': 4, 'defense': 10, 'shield': 2, 'speed': 8},
                    {'name': 'Crusher', 'type': 'BRAWLER', 'rarity': 'Common', 'lvl': 3, 'hp': 110, 'physical': 16, 'energy': 4, 'defense': 8, 'shield': 2, 'speed': 6},
                    {'name': 'Gnasher', 'type': 'BRAWLER', 'rarity': 'Uncommon', 'lvl': 2, 'hp': 95, 'physical': 12, 'energy': 6, 'defense': 8, 'shield': 6, 'speed': 10},
                ],
            },
            {
                'call_sign': 'STATIC',
                'title': 'Noise Maker',
                'floor': 5,
                'difficulty_rating': 3,
                'is_gate_boss': False,
                'unlocks_rank': '',
                'bio': "Specializing in electronic warfare, STATIC's cores emit disruptive frequencies that scramble targeting systems. What you can't lock onto, you can't hit.",
                'reward_bits': 100,
                'reward_exp': 50,
                'win_mail_subject': '~*SIGNAL LOST*~',
                'win_mail_body': "Y0u bR0k3 tHr0uGh mY jAmMiNg... ImPr3sS1v3. -STATIC",
                'lose_mail_subject': '~*NO SIGNAL*~',
                'lose_mail_body': "CaN't HiT wH4t Y0u CaN't S33... -STATIC",
                'cores': [
                    {'name': 'Interference-1', 'type': 'DISRUPTOR', 'rarity': 'Uncommon', 'lvl': 3, 'hp': 75, 'physical': 6, 'energy': 16, 'defense': 6, 'shield': 14, 'speed': 14},
                    {'name': 'White Noise', 'type': 'DISRUPTOR', 'rarity': 'Common', 'lvl': 3, 'hp': 85, 'physical': 8, 'energy': 14, 'defense': 8, 'shield': 10, 'speed': 12},
                    {'name': 'Feedback', 'type': 'DISRUPTOR', 'rarity': 'Common', 'lvl': 2, 'hp': 80, 'physical': 10, 'energy': 12, 'defense': 10, 'shield': 8, 'speed': 10},
                ],
            },
            {
                'call_sign': 'COBALT',
                'title': 'Cold Steel',
                'floor': 4,
                'difficulty_rating': 3,
                'is_gate_boss': False,
                'unlocks_rank': '',
                'bio': "A former corporate security operative gone freelance. COBALT's military-grade cores are well-maintained and combat-tested. Professional, precise, and utterly without mercy.",
                'reward_bits': 100,
                'reward_exp': 50,
                'win_mail_subject': 'Acknowledged',
                'win_mail_body': "A clean victory. Your form showed promise. Consider this a professional courtesy. -COBALT",
                'lose_mail_subject': 'Debrief',
                'lose_mail_body': "Engagement concluded. Target neutralized efficiently. No further action required. -COBALT",
                'cores': [
                    {'name': 'Sentinel-A7', 'type': 'MILITARY', 'rarity': 'Uncommon', 'lvl': 3, 'hp': 95, 'physical': 12, 'energy': 12, 'defense': 12, 'shield': 10, 'speed': 10},
                    {'name': 'Guardian-B3', 'type': 'MILITARY', 'rarity': 'Uncommon', 'lvl': 4, 'hp': 105, 'physical': 10, 'energy': 10, 'defense': 14, 'shield': 12, 'speed': 8},
                    {'name': 'Warden-C1', 'type': 'MILITARY', 'rarity': 'Common', 'lvl': 3, 'hp': 90, 'physical': 14, 'energy': 8, 'defense': 10, 'shield': 8, 'speed': 12},
                ],
            },
            {
                'call_sign': 'PISTON',
                'title': 'Engine Heart',
                'floor': 3,
                'difficulty_rating': 4,
                'is_gate_boss': False,
                'unlocks_rank': '',
                'bio': "Born in the engine rooms of cargo haulers, PISTON brings raw mechanical power to the arena. Their cores may be loud and smoky, but they hit like a freight train.",
                'reward_bits': 125,
                'reward_exp': 60,
                'win_mail_subject': 'ENGINE TROUBLE',
                'win_mail_body': "Looks like my rig stalled out before I could finish you. Don't expect the same luck twice! -PISTON",
                'lose_mail_subject': 'FULL THROTTLE',
                'lose_mail_body': "VROOM VROOM! Can't keep up with pure horsepower, can ya? -PISTON",
                'cores': [
                    {'name': 'Diesel-Rex', 'type': 'HEAVY', 'rarity': 'Uncommon', 'lvl': 4, 'hp': 120, 'physical': 16, 'energy': 6, 'defense': 14, 'shield': 4, 'speed': 6},
                    {'name': 'Turbo-Mk2', 'type': 'HEAVY', 'rarity': 'Uncommon', 'lvl': 3, 'hp': 100, 'physical': 14, 'energy': 8, 'defense': 10, 'shield': 6, 'speed': 12},
                    {'name': 'Crank-V8', 'type': 'HEAVY', 'rarity': 'Common', 'lvl': 4, 'hp': 115, 'physical': 12, 'energy': 6, 'defense': 12, 'shield': 8, 'speed': 8},
                ],
            },
            {
                'call_sign': 'RAZOR',
                'title': 'Cutting Edge',
                'floor': 2,
                'difficulty_rating': 4,
                'is_gate_boss': False,
                'unlocks_rank': '',
                'bio': "Speed kills, and RAZOR is the fastest in E-rank. Their lightweight cores sacrifice armor for agility, striking before opponents can react.",
                'reward_bits': 125,
                'reward_exp': 60,
                'win_mail_subject': 'Too Slow',
                'win_mail_body': "Huh. You actually tagged me. That doesn't happen often. Keep it up. -RAZOR",
                'lose_mail_subject': 'Blink',
                'lose_mail_body': "Did you even see me coming? Probably not. -RAZOR",
                'cores': [
                    {'name': 'Blade-Zero', 'type': 'STRIKER', 'rarity': 'Uncommon', 'lvl': 4, 'hp': 70, 'physical': 16, 'energy': 12, 'defense': 4, 'shield': 4, 'speed': 18},
                    {'name': 'Edge-Prime', 'type': 'STRIKER', 'rarity': 'Uncommon', 'lvl': 4, 'hp': 75, 'physical': 14, 'energy': 14, 'defense': 6, 'shield': 6, 'speed': 16},
                    {'name': 'Scalpel-X', 'type': 'STRIKER', 'rarity': 'Rare', 'lvl': 3, 'hp': 65, 'physical': 12, 'energy': 16, 'defense': 4, 'shield': 8, 'speed': 20},
                ],
            },
            {
                'call_sign': 'ANVIL',
                'title': 'Hammerdown',
                'floor': 1,  # Gate boss - top of E-rank
                'difficulty_rating': 5,
                'is_gate_boss': True,
                'unlocks_rank': 'D',
                'bio': "The gatekeeper of E-rank. ANVIL has crushed countless challengers seeking to advance. Their fortress-like cores can absorb tremendous punishment while dealing devastating blows. Only the worthy pass.",
                'reward_bits': 200,
                'reward_exp': 100,
                'win_mail_subject': 'Worthy Challenger',
                'win_mail_body': "You broke through my defense. That takes skill—and guts. D-rank awaits you. Don't disappoint. -ANVIL",
                'lose_mail_subject': 'The Wall Stands',
                'lose_mail_body': "Another one falls at the gate. Come back stronger, or don't come back at all. -ANVIL",
                'cores': [
                    {'name': 'Fortress-Alpha', 'type': 'TANK', 'rarity': 'Rare', 'lvl': 5, 'hp': 140, 'physical': 14, 'energy': 8, 'defense': 18, 'shield': 14, 'speed': 4},
                    {'name': 'Bastion-Beta', 'type': 'TANK', 'rarity': 'Uncommon', 'lvl': 5, 'hp': 130, 'physical': 12, 'energy': 10, 'defense': 16, 'shield': 12, 'speed': 6},
                    {'name': 'Bulwark-Gamma', 'type': 'TANK', 'rarity': 'Uncommon', 'lvl': 4, 'hp': 125, 'physical': 16, 'energy': 6, 'defense': 14, 'shield': 10, 'speed': 8},
                ],
            },
        ]

        # Create NPCs
        created_count = 0
        for npc_data in npcs_data:
            cores_data = npc_data.pop('cores')

            npc = NPCOperator.objects.create(
                arena_rank='E',
                **npc_data
            )
            self.stdout.write(f"Created NPC: {npc.call_sign}")

            # Create cores
            for i, core_data in enumerate(cores_data):
                core = NPCCore.objects.create(
                    npc_operator=npc,
                    name=core_data['name'],
                    core_type=core_data['type'],
                    rarity=core_data['rarity'],
                    lvl=core_data['lvl'],
                    team_position=i,
                    hp=core_data['hp'],
                    physical=core_data['physical'],
                    energy=core_data['energy'],
                    defense=core_data['defense'],
                    shield=core_data['shield'],
                    speed=core_data['speed'],
                )

                # Assign moves based on core position and type
                core_moves = []
                if core_data['type'] in ['BRAWLER', 'HEAVY', 'TANK']:
                    # Physical-focused cores
                    if basic_physical:
                        core_moves.extend(basic_physical[:2])
                    if defensive:
                        core_moves.append(defensive[0])
                elif core_data['type'] in ['TECH', 'DISRUPTOR', 'STRIKER']:
                    # Energy-focused cores
                    if basic_energy:
                        core_moves.extend(basic_energy[:2])
                    if defensive and len(defensive) > 1:
                        core_moves.append(defensive[1])
                else:
                    # Balanced/other cores
                    if basic_physical:
                        core_moves.append(basic_physical[0])
                    if basic_energy:
                        core_moves.append(basic_energy[0])
                    if defensive:
                        core_moves.append(defensive[0])

                # Add support move for lead core (position 0)
                if i == 0 and support:
                    core_moves.append(support[0])

                # Create equipped moves (max 4 slots)
                for slot, move in enumerate(core_moves[:4], start=1):
                    if move:
                        NPCCoreEquippedMove.objects.create(
                            npc_core=core,
                            move=move,
                            slot=slot
                        )

                self.stdout.write(f"  - Core: {core.name} with {len(core_moves[:4])} moves")

            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {created_count} E-rank NPCs with cores and moves!'
        ))
