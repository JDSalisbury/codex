#!/usr/bin/env python
"""Quick test script for core generation backend logic"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from codex.models import Operator, Garage, Core
from codex.services.core_factory import generate_core, CoreGenRequest
from codex.constants import RARITY_PRICES

print("=" * 60)
print("TESTING CORE GENERATION BACKEND")
print("=" * 60)

# Get or create a test operator
operator, created = Operator.objects.get_or_create(
    call_sign="TestOperator",
    defaults={
        'bits': 10000,
        'lvl': 1,
        'rank': 'F'
    }
)

if created:
    print(f"\n✓ Created test operator: {operator.call_sign}")
else:
    print(f"\n✓ Using existing operator: {operator.call_sign}")
    # Make sure operator has enough bits
    if operator.bits < 100:
        operator.bits = 10000
        operator.save()
        print(f"  → Reset bits to {operator.bits}")

print(f"  → Operator ID: {operator.id}")
print(f"  → Bits: {operator.bits}")
print(f"  → Level: {operator.lvl}")

# Get or create garage
try:
    garage = operator.garage
    print(f"\n✓ Using existing garage: {garage.id}")
except Garage.DoesNotExist:
    garage = Garage.objects.create(operator=operator, bay_doors=3)
    print(f"\n✓ Created garage: {garage.id}")

print(f"  → Capacity: {garage.bay_doors}")
print(f"  → Active cores: {garage.cores.filter(decommed=False).count()}")

# Test core generation
print("\n" + "=" * 60)
print("GENERATING TEST CORE")
print("=" * 60)

core_request = CoreGenRequest(
    name="Test Combat Frame",
    core_type="",  # Randomly assigned
    rarity="Common",
    track="Balanced",
    price=RARITY_PRICES["Common"]
)

print(f"\n→ Request:")
print(f"  Name: {core_request.name}")
print(f"  Rarity: {core_request.rarity}")
print(f"  Track: {core_request.track}")
print(f"  Price: {core_request.price}")

try:
    # Generate core
    core = generate_core(garage, core_request)

    # Deduct bits
    operator.bits -= core_request.price
    operator.save()

    print(f"\n✓ Core generated successfully!")
    print(f"  → Core ID: {core.id}")
    print(f"  → Name: {core.name}")
    print(f"  → Type: {core.type} (randomly assigned)")
    print(f"  → Rarity: {core.rarity}")
    print(f"  → Level: {core.lvl}")
    print(f"  → Price: {core.price}")

    print(f"\n→ Battle Stats:")
    print(f"  HP: {core.battle_info.hp}")
    print(f"  Physical: {core.battle_info.physical}")
    print(f"  Energy: {core.battle_info.energy}")
    print(f"  Defense: {core.battle_info.defense}")
    print(f"  Shield: {core.battle_info.shield}")
    print(f"  Speed: {core.battle_info.speed}")
    print(f"  Equip Slots: {core.battle_info.equip_slots}")

    print(f"\n→ Upgrade Info:")
    print(f"  EXP: {core.upgrade_info.exp}")
    print(f"  Next Level: {core.upgrade_info.next_lvl}")
    print(f"  Tracks: {core.upgrade_info.tracks}")

    print(f"\n→ Operator after generation:")
    operator.refresh_from_db()
    print(f"  Bits: {operator.bits} (spent {core_request.price})")

    print(f"\n→ Garage status:")
    active_cores = garage.cores.filter(decommed=False).count()
    print(f"  Active cores: {active_cores}/{garage.bay_doors}")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗ TEST FAILED")
    print("=" * 60)
