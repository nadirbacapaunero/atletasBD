from datetime import datetime
from types import SimpleNamespace

import pytest
from src import obsidian_writer
from src.obsidian_writer import ObsidianVaultWriter


class DummyAthleteCollection:
    def __init__(self, athlete):
        self.athlete = athlete

    def find_one(self, query):
        return self.athlete


def test_generate_athlete_profile_writes_markdown(tmp_path):
    writer = ObsidianVaultWriter(tmp_path)
    athlete_data = {
        "name": "Juan Perez",
        "strava_id": 123,
        "metadata": {"ftp": 250, "lthr": 170, "weight": 70, "max_hr": 190},
        "sync_status": "active",
        "last_sync": "2024-01-01"
    }

    writer.generate_athlete_profile("athlete_1", athlete_data)
    filepath = tmp_path / "Atletas" / "Juan_Perez.md"

    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8")
    assert "Juan Perez" in content
    assert "FTP (W)" in content
    assert "LTHR (bpm)" in content


def test_generate_activity_note_uses_athlete_name(tmp_path, monkeypatch):
    writer = ObsidianVaultWriter(tmp_path)
    monkeypatch.setattr(obsidian_writer, "db", SimpleNamespace(athletes_collection=DummyAthleteCollection({"name": "Juan Perez"})))

    activity_data = {
        "name": "Entrenamiento 1",
        "date": datetime(2024, 1, 1, 10, 0),
        "type": "Run",
        "distance_m": 5000,
        "duration_seconds": 1800,
        "avg_speed_ms": 3.0,
        "avg_heart_rate": 150,
        "max_heart_rate": 165,
        "elevation_m": 50,
        "metrics": {"tss": 40},
        "notes": "Buen ritmo",
        "athlete_id": "athlete_1"
    }

    writer.generate_activity_note(activity_data)
    filepath = tmp_path / "Actividades" / "2024-01-01 10:00_Entrenamiento_1.md"

    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8")
    assert "Entrenamiento 1" in content
    assert "Juan Perez" in content
    assert "Velocidad Promedio" in content


def test_generate_daily_metrics_includes_status_text(tmp_path):
    writer = ObsidianVaultWriter(tmp_path)
    metrics_data = {
        "metrics": {
            "cTL": 100,
            "aTL": 80,
            "tSB": 20,
            "weekly_tss": 250,
            "status": "peak",
            "total_distance_m": 12000,
            "total_elevation_m": 250,
            "avg_hr": 155,
            "sport_breakdown": {
                "Run": {"tss": 100, "distance": 7000},
                "Ride": {"tss": 150, "distance": 5000}
            }
        }
    }

    writer.generate_daily_metrics("athlete_1", "Juan Perez", metrics_data)
    filename = f"Juan_Perez_{datetime.utcnow().strftime('%Y-%m-%d')}_Metrics.md"
    filepath = tmp_path / "Métricas" / filename

    assert filepath.exists()
    content = filepath.read_text(encoding="utf-8")
    assert "Juan Perez" in content
    assert "ÓPTIMO PARA COMPETENCIA" in content
