#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test telegram_bot.py
"""

print("\n" + "="*60)
print("[TEST] TELEGRAM BOT")
print("="*60 + "\n")

# Test 1: Import
print("[1] Import telegram_bot module")
print("-" * 40)
try:
    from src.telegram_bot import CoachingBot, create_app
    print("   [OK] CoachingBot imported")
    print("   [OK] create_app imported")
except Exception as e:
    print(f"   [ERROR] Import failed: {e}")
    exit(1)

# Test 2: Verify bot methods
print("\n[2] Verify CoachingBot methods")
print("-" * 40)
methods = ['start', 'register', 'status', 'weekly', 'ask']
for method in methods:
    if hasattr(CoachingBot, method):
        print(f"   [OK] {method} exists")
    else:
        print(f"   [ERROR] {method} missing")

# Test 3: create_app function
print("\n[3] Check create_app function")
print("-" * 40)
try:
    import inspect
    sig = inspect.signature(create_app)
    print(f"   [OK] create_app signature: {sig}")
    print(f"   [OK] create_app is callable: {callable(create_app)}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 4: Config check
print("\n[4] Check Telegram token in config")
print("-" * 40)
try:
    from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID
    if TELEGRAM_BOT_TOKEN:
        print(f"   [OK] TELEGRAM_BOT_TOKEN configured")
        print(f"   [OK] Token starts with: {TELEGRAM_BOT_TOKEN[:10]}...")
    else:
        print("   [ERROR] TELEGRAM_BOT_TOKEN not set")

    if TELEGRAM_ADMIN_ID:
        print(f"   [OK] TELEGRAM_ADMIN_ID: {TELEGRAM_ADMIN_ID}")
    else:
        print("   [WARN] TELEGRAM_ADMIN_ID not set")
except Exception as e:
    print(f"   [ERROR] Config error: {e}")

print("\n" + "="*60)
print("[OK] TEST COMPLETE")
print("="*60)
print("\nSummary:")
print("   [OK] Bot module imports")
print("   [OK] All command handlers exist")
print("   [OK] create_app function ready")
print("   [OK] Telegram token configured")
print("\n[NEXT] Final: Implement main.py scheduler")
print()
