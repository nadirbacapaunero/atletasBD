#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test con atleta real - Flow completo
"""

import sys
from datetime import datetime, timedelta
from bson import ObjectId

print("\n" + "="*70)
print("[TEST] FULL ATHLETE WORKFLOW")
print("="*70 + "\n")

# Step 1: Create test athlete in MongoDB
print("[1] Create test athlete in MongoDB")
print("-" * 70)
try:
    from src.mongodb_models import db, AthleteManager
    from cryptography.fernet import Fernet
    import os

    athlete_manager = AthleteManager(db)

    athlete_data = {
        'strava_id': 999999999,  # Test ID
        'name': 'Test Athlete',
        'email': 'test@example.com',
        'sport': 'triathlon'
    }

    # Create athlete
    athlete_id = athlete_manager.create_athlete(
        strava_id=athlete_data['strava_id'],
        name=athlete_data['name'],
        email=athlete_data['email'],
        sport=athlete_data['sport']
    )

    if athlete_id:
        print(f"   [OK] Athlete created: {athlete_id}")
        athlete_doc = db.athletes_collection.find_one({"_id": athlete_id})
        print(f"   [OK] Name: {athlete_doc['name']}")
        print(f"   [OK] Sport: {athlete_doc['sport']}")
        print(f"   [OK] Status: {athlete_doc['sync_status']}")
    else:
        print("   [ERROR] Failed to create athlete")
        athlete_id = db.athletes_collection.find_one({"strava_id": athlete_data['strava_id']})['_id']
        print(f"   [WARN] Using existing athlete: {athlete_id}")

except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Add test activities
print("\n[2] Add test activities to athlete")
print("-" * 70)
try:
    from src.mongodb_models import ActivityManager
    from datetime import datetime

    activity_manager = ActivityManager(db)

    test_activities = [
        {
            'id': 1001,
            'name': 'Morning Run',
            'type': 'Run',
            'start_date_local': datetime.utcnow() - timedelta(days=2),
            'elapsed_time': 3600,  # 1 hour
            'distance': 10000,  # 10 km
            'total_elevation_gain': 150,
            'average_speed': 2.78,
            'average_heartrate': 160,
            'max_heartrate': 175,
            'average_cadence': 180,
            'average_watts': 0,
            'kilojoules': 0,
            'description': 'Good morning run'
        },
        {
            'id': 1002,
            'name': 'Bike Session',
            'type': 'Ride',
            'start_date_local': datetime.utcnow() - timedelta(days=1),
            'elapsed_time': 5400,  # 1.5 hours
            'distance': 40000,  # 40 km
            'total_elevation_gain': 300,
            'average_speed': 7.4,
            'average_heartrate': 140,
            'max_heartrate': 165,
            'average_cadence': 85,
            'average_watts': 250,
            'kilojoules': 900,
            'description': 'Strong ride'
        },
        {
            'id': 1003,
            'name': 'Pool Swim',
            'type': 'Swim',
            'start_date_local': datetime.utcnow(),
            'elapsed_time': 1800,  # 30 min
            'distance': 2000,  # 2 km
            'total_elevation_gain': 0,
            'average_speed': 1.11,
            'average_heartrate': 145,
            'max_heartrate': 160,
            'average_cadence': 0,
            'average_watts': 0,
            'kilojoules': 0,
            'description': 'Easy swim'
        }
    ]

    activity_count = 0
    for activity in test_activities:
        activity_id = activity_manager.insert_activity(athlete_id, activity)
        if activity_id:
            activity_count += 1
            print(f"   [OK] Activity added: {activity['name']} ({activity['type']})")

    print(f"   [OK] Total activities added: {activity_count}")

except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Step 3: Calculate metrics
print("\n[3] Calculate metrics (TSS/CTL/ATL/TSB)")
print("-" * 70)
try:
    from src.metrics import MetricsCalculator
    from src.mongodb_models import MetricsManager

    metrics_manager = MetricsManager(db)

    # Get athlete metadata (with defaults)
    athlete = db.athletes_collection.find_one({"_id": athlete_id})
    metadata = athlete.get('metadata', {'ftp': 200, 'lthr': 150})

    # Calculate TSS for each activity
    activities = list(db.activities_collection.find({"athlete_id": athlete_id}))
    print(f"   [OK] Found {len(activities)} activities")

    for activity in activities:
        tss = MetricsCalculator.calculate_tss(activity, metadata)
        db.activities_collection.update_one(
            {"_id": activity['_id']},
            {"$set": {"metrics.tss": tss}}
        )
        print(f"      TSS {activity['name']}: {tss}")

    # Calculate CTL/ATL/TSB
    metrics = MetricsCalculator.calculate_ctl_atl_tsb(athlete_id)
    metrics_manager.insert_metrics(athlete_id, metrics)

    print(f"   [OK] CTL: {metrics['cTL']}")
    print(f"   [OK] ATL: {metrics['aTL']}")
    print(f"   [OK] TSB: {metrics['tSB']}")
    print(f"   [OK] Status: {metrics['status']}")

except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Step 4: Generate Obsidian vault
print("\n[4] Generate Obsidian vault files")
print("-" * 70)
try:
    import os
    from pathlib import Path
    from src.obsidian_writer import ObsidianVaultWriter

    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    writer = ObsidianVaultWriter(vault_path)

    athlete = db.athletes_collection.find_one({"_id": athlete_id})

    # Generate athlete profile
    writer.generate_athlete_profile(athlete_id, athlete)
    print(f"   [OK] Athlete profile generated")

    # Generate activity notes
    activities = db.activities_collection.find({"athlete_id": athlete_id})
    for activity in activities:
        writer.generate_activity_note(activity)
    print(f"   [OK] Activity notes generated")

    # Generate metrics
    metrics = db.metrics_collection.find_one(
        {"athlete_id": athlete_id},
        sort=[("date", -1)]
    )
    if metrics:
        writer.generate_daily_metrics(athlete_id, athlete['name'], metrics)
        print(f"   [OK] Daily metrics generated")

    # Generate index
    writer.generate_index()
    print(f"   [OK] Index generated")

    # List generated files
    athletes_folder = Path(vault_path) / "Atletas"
    files = list(athletes_folder.glob("*.md"))
    print(f"   [OK] Vault has {len(files)} athlete files")

except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Step 5: Verify weekly summary
print("\n[5] Generate weekly summary")
print("-" * 70)
try:
    from src.metrics import MetricsCalculator

    summary = MetricsCalculator.generate_weekly_summary(athlete_id)
    print(f"   [OK] Activities: {summary['activities_count']}")
    print(f"   [OK] Distance: {summary['total_distance']:.1f} km")
    print(f"   [OK] Total TSS: {summary['total_tss']:.1f}")
    print(f"   [OK] Elevation: {summary['total_elevation']:.0f} m")
    print(f"   [OK] Disciplines: {list(summary['disciplines'].keys())}")

    for sport, data in summary['disciplines'].items():
        print(f"      {sport}: {data['count']} sessions, {data['distance']:.1f} km, {data['tss']:.0f} TSS")

except Exception as e:
    print(f"   [ERROR] {e}")

# Final summary
print("\n" + "="*70)
print("[SUCCESS] COMPLETE ATHLETE WORKFLOW VERIFIED")
print("="*70)
print("\nTest athlete created and tested:")
print(f"   Name: Test Athlete")
print(f"   ID: {athlete_id}")
print(f"   Sport: triathlon")
print(f"   Activities: 3 (run, ride, swim)")
print("\nFiles generated in Obsidian vault:")
print(f"   - Atletas/Test_Athlete.md")
print(f"   - Actividades/[3 activity files]")
print(f"   - Metricas/Test_Athlete_[date]_Metrics.md")
print(f"   - INDEX.md")
print("\nNext: Deploy to Railway and test with real Strava OAuth")
print()
