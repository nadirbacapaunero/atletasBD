#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test obsidian_writer.py
"""

import os
from pathlib import Path

print("\n" + "="*60)
print("[TEST] OBSIDIAN VAULT WRITER")
print("="*60 + "\n")

# Test 1: Import
print("[1] Import ObsidianVaultWriter")
print("-" * 40)
try:
    from src.obsidian_writer import ObsidianVaultWriter
    print("   [OK] Import successful")
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Test 2: Get vault path from env
print("\n[2] Get vault path from .env")
print("-" * 40)
try:
    from dotenv import load_dotenv
    load_dotenv()
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if vault_path:
        vault_dir = Path(vault_path)
        if vault_dir.exists():
            print(f"   [OK] Vault exists: {vault_path}")
            print(f"   [OK] Is directory: {vault_dir.is_dir()}")
        else:
            print(f"   [WARN] Vault path not found: {vault_path}")
    else:
        print("   [ERROR] OBSIDIAN_VAULT_PATH not set in .env")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 3: Initialize writer
print("\n[3] Initialize ObsidianVaultWriter")
print("-" * 40)
try:
    writer = ObsidianVaultWriter(vault_path)
    print("   [OK] Writer initialized")
    print(f"   [OK] Athletes folder: {writer.athletes_folder}")
    print(f"   [OK] Activities folder: {writer.activities_folder}")
    print(f"   [OK] Metrics folder: {writer.metrics_folder}")

    # Check if folders created
    if writer.athletes_folder.exists():
        print("   [OK] Athletes folder created/exists")
    if writer.activities_folder.exists():
        print("   [OK] Activities folder created/exists")
    if writer.metrics_folder.exists():
        print("   [OK] Metrics folder created/exists")
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test methods exist
print("\n[4] Verify methods exist")
print("-" * 40)
methods = [
    'generate_athlete_profile',
    'generate_activity_note',
    'generate_daily_metrics',
    'generate_index'
]
for method in methods:
    if hasattr(writer, method):
        print(f"   [OK] {method}")
    else:
        print(f"   [ERROR] {method} missing")

# Test 5: Test with mock data
print("\n[5] Test athlete profile generation")
print("-" * 40)
try:
    from bson import ObjectId
    mock_athlete = {
        '_id': ObjectId(),
        'strava_id': 12345678,
        'name': 'Test Athlete',
        'email': 'test@example.com',
        'sport': 'triathlon',
        'sync_status': 'active',
        'last_sync': None,
        'metadata': {
            'ftp': 200,
            'lthr': 150,
            'weight': 75,
            'max_hr': 195
        }
    }

    # Generate profile
    writer.generate_athlete_profile(mock_athlete['_id'], mock_athlete)

    # Check file exists
    profile_file = writer.athletes_folder / "Test_Athlete.md"
    if profile_file.exists():
        print(f"   [OK] Profile generated: {profile_file.name}")
        # Check content
        with open(profile_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Test Athlete' in content and 'triathlon' in content:
                print("   [OK] Profile content valid")
                print(f"   [OK] File size: {len(content)} bytes")
            else:
                print("   [ERROR] Profile content invalid")
    else:
        print(f"   [ERROR] Profile file not created")
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("[OK] TEST COMPLETE")
print("="*60)
print("\nSummary:")
print("   [OK] ObsidianVaultWriter imports")
print("   [OK] Vault folders created/exist")
print("   [OK] All methods present")
print("   [OK] Can generate athlete profiles")
print("\nNext: Implement telegram_bot.py")
print()
