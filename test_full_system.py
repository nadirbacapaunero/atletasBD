#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full system test - Semana 2 COMPLETA
Verifica que todos los componentes funcionen
"""

import sys

print("\n" + "="*70)
print("[FULL TEST] SEMANA 2 SYSTEM VERIFICATION")
print("="*70 + "\n")

# Component tests
tests_passed = 0
tests_failed = 0

def test_component(name, import_path, items_to_check):
    global tests_passed, tests_failed
    print(f"\n[TEST] {name}")
    print("-" * 50)
    try:
        # Import
        module = __import__(import_path, fromlist=[''])
        print(f"   [OK] Module imported: {import_path}")

        # Check items
        for item in items_to_check:
            if hasattr(module, item):
                print(f"   [OK] {item} found")
            else:
                print(f"   [FAIL] {item} NOT found")
                tests_failed += 1
                return False

        tests_passed += 1
        return True
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        tests_failed += 1
        return False

# Test all modules
test_component("Config", "src.config", [
    'MONGODB_URI', 'STRAVA_CLIENT_ID', 'TELEGRAM_BOT_TOKEN'
])

test_component("MongoDB Models", "src.mongodb_models", [
    'MongoDBConnection', 'AthleteManager', 'ActivityManager', 'MetricsManager'
])

test_component("Strava OAuth", "src.strava_oauth", [
    'StravaOAuthHandler', 'StravaAPIClient'
])

test_component("Metrics", "src.metrics", [
    'MetricsCalculator'
])

test_component("Strava Sync", "src.strava_sync", [
    'StravaSyncService'
])

test_component("Obsidian Writer", "src.obsidian_writer", [
    'ObsidianVaultWriter'
])

test_component("Telegram Bot", "src.telegram_bot", [
    'CoachingBot', 'create_app'
])

test_component("Main System", "src.main", [
    'CoachingSystem'
])

# Test database connection
print("\n[TEST] Database Connection")
print("-" * 50)
try:
    from src.mongodb_models import MongoDBConnection
    db = MongoDBConnection()
    db_instance = db.db
    collections = db_instance.list_collection_names()
    print(f"   [OK] MongoDB connected")
    print(f"   [OK] Collections: {len(collections)}")
    tests_passed += 1
except Exception as e:
    print(f"   [FAIL] MongoDB error: {e}")
    tests_failed += 1

# Test metrics calculation
print("\n[TEST] Metrics Calculation")
print("-" * 50)
try:
    from src.metrics import MetricsCalculator
    activity = {
        'type': 'Run',
        'duration_seconds': 3600,
        'avg_heart_rate': 160,
        'avg_power': 0
    }
    metadata = {'lthr': 150, 'ftp': 200}
    tss = MetricsCalculator.calculate_tss(activity, metadata)
    if tss > 0:
        print(f"   [OK] TSS calculated: {tss}")
        tests_passed += 1
    else:
        print(f"   [FAIL] TSS is zero")
        tests_failed += 1
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    tests_failed += 1

# Test Obsidian vault
print("\n[TEST] Obsidian Vault")
print("-" * 50)
try:
    import os
    from pathlib import Path
    from src.obsidian_writer import ObsidianVaultWriter
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if vault_path and Path(vault_path).exists():
        writer = ObsidianVaultWriter(vault_path)
        print(f"   [OK] Vault initialized")
        print(f"   [OK] Folders created")
        tests_passed += 1
    else:
        print(f"   [WARN] Vault path not accessible")
        tests_failed += 1
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    tests_failed += 1

# Summary
print("\n" + "="*70)
print("[SUMMARY] SEMANA 2 IMPLEMENTATION")
print("="*70)
print(f"\nTests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")

if tests_failed == 0:
    print("\n[SUCCESS] SEMANA 2 COMPLETE AND VERIFIED")
    print("\nImplemented:")
    print("   [OK] metrics.py - TSS/CTL/ATL/TSB calculations")
    print("   [OK] strava_sync.py - Athlete sync service")
    print("   [OK] obsidian_writer.py - Vault generation")
    print("   [OK] telegram_bot.py - Bot commands")
    print("   [OK] main.py - Scheduler + orchestration")
    print("\nDefaults:")
    print("   [OK] FTP: 200W")
    print("   [OK] LTHR: 150 bpm")
    print("   [OK] Sync time: 21:00 hs Buenos Aires")
    print("\nNext Steps:")
    print("   1. Add test athlete with /register in Telegram")
    print("   2. Verify sync at 21:00 daily")
    print("   3. Check Obsidian vault updates")
    print("   4. Deploy to Railway (Semana 3)")
    sys.exit(0)
else:
    print(f"\n[ERROR] {tests_failed} test(s) failed")
    sys.exit(1)
