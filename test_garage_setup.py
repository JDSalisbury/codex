#!/usr/bin/env python
"""Test script to verify operator initialization and garage setup"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from codex.models import Operator, Garage, Core

# Create a test operator
print("Creating test operator...")
operator = Operator.objects.create(call_sign="TEST_GARAGE")

# Check if garage was created
print(f"Operator created: {operator.id}")
print(f"Operator call sign: {operator.call_sign}")
print(f"Operator bits: {operator.bits}")

if hasattr(operator, 'garage'):
    print(f"✓ Garage created automatically: {operator.garage.id}")
    print(f"  Bay doors: {operator.garage.bay_doors}")

    # Check for cores
    cores = operator.garage.cores.filter(decommed=False)
    print(f"  Active cores: {cores.count()}")

    if cores.exists():
        for core in cores:
            print(f"\n  Core Details:")
            print(f"    Name: {core.name}")
            print(f"    Level: {core.lvl}")
            print(f"    Rarity: {core.rarity}")
            print(f"    Type: {core.type}")
            print(f"    Price: {core.price}")

            if hasattr(core, 'battle_info'):
                print(f"    ✓ Battle info exists")
                print(f"      HP: {core.battle_info.hp_current}/{core.battle_info.hp_max}")
                print(f"      Physical: {core.battle_info.physical_attack}")
                print(f"      Energy: {core.battle_info.energy_attack}")
                print(f"      Defense: {core.battle_info.defense}")
                print(f"      Shield: {core.battle_info.shield}")
                print(f"      Speed: {core.battle_info.speed}")

            if hasattr(core, 'upgrade_info'):
                print(f"    ✓ Upgrade info exists")
                print(f"      EXP: {core.upgrade_info.exp}/{core.upgrade_info.next_lvl}")
    else:
        print("  ✗ No cores found!")
else:
    print("✗ Garage was NOT created!")

print("\n" + "="*50)
print("Testing API endpoints...")
print("="*50)

# Test if we can query cores by garage
cores_by_garage = Core.objects.filter(garage=operator.garage, decommed=False)
print(f"\nCores filtered by garage: {cores_by_garage.count()}")

print("\nAPI Endpoints you can now use:")
print(f"  GET /codex/operators/{operator.id}/")
print(f"  GET /codex/garages/{operator.garage.id}/")
print(f"  GET /codex/cores/?garage={operator.garage.id}&decommed=false")

print("\nTest complete!")
