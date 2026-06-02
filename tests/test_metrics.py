from datetime import datetime, timedelta

from src.metrics import MetricsCalculator


def test_calculate_tss_run_uses_hr():
    activity = {
        "type": "Run",
        "duration_seconds": 60 * 30,
        "avg_heart_rate": 160
    }
    athlete_metadata = {"lthr": 160}

    result = MetricsCalculator.calculate_tss(activity, athlete_metadata)
    assert result > 0
    assert isinstance(result, float)


def test_calculate_tss_ride_uses_power():
    activity = {
        "type": "Ride",
        "duration_seconds": 60 * 60,
        "avg_power": 200
    }
    athlete_metadata = {"ftp": 200}

    result = MetricsCalculator.calculate_tss(activity, athlete_metadata)
    assert result == 100.0


def test_calculate_tss_fallback_returns_duration_scaled():
    activity = {
        "type": "Run",
        "duration_seconds": 60 * 20,
    }
    athlete_metadata = {}

    result = MetricsCalculator.calculate_tss(activity, athlete_metadata)
    assert result == 16.0


def test_get_training_status_boundaries():
    assert MetricsCalculator.get_training_status(100, 50, 50) == "overreaching"
    assert MetricsCalculator.get_training_status(100, 90, 10) == "peak"
    assert MetricsCalculator.get_training_status(100, 95, 0) == "training"
    assert MetricsCalculator.get_training_status(100, 130, -30) == "fatigued"
