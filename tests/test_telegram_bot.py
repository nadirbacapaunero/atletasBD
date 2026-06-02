import asyncio
from types import SimpleNamespace

from src.telegram_bot import CoachingBot


class FakeMessage:
    def __init__(self):
        self.chat_id = 1234
        self.replies = []

    async def reply_text(self, text, parse_mode=None):
        self.replies.append((text, parse_mode))


class FakeUpdate:
    def __init__(self):
        self.message = FakeMessage()
        self.effective_user = SimpleNamespace(id=99, first_name="Test", username="tester")


class FakeSessionsCollection:
    def __init__(self):
        self.calls = []

    def update_one(self, query, update, upsert=False):
        self.calls.append((query, update, upsert))


def test_register_saves_session_and_sends_link(monkeypatch):
    fake_db = SimpleNamespace(sessions_collection=FakeSessionsCollection())
    monkeypatch.setattr("src.telegram_bot.db", fake_db)
    monkeypatch.setattr("src.telegram_bot.StravaOAuthHandler.get_authorization_url", lambda athlete_id: "https://strava.example/auth")

    update = FakeUpdate()
    context = SimpleNamespace(args=[])
    asyncio.run(CoachingBot.register(update, context))

    assert len(fake_db.sessions_collection.calls) == 1
    assert fake_db.sessions_collection.calls[0][0] == {"telegram_user_id": 99}
    assert "https://strava.example/auth" in update.message.replies[0][0]


def test_sync_triggers_sync_service_and_obsidian(monkeypatch):
    fake_db = SimpleNamespace(
        sessions_collection=SimpleNamespace(
            find_one=lambda query: {"telegram_user_id": 99, "athlete_id": "athlete123"}
        ),
        athletes_collection=SimpleNamespace(
            find_one=lambda query: {"_id": "athlete123", "strava_id": 42}
        )
    )
    monkeypatch.setattr("src.telegram_bot.db", fake_db)
    monkeypatch.setattr("src.telegram_bot.StravaSyncService", lambda: SimpleNamespace(sync_athlete=lambda athlete_id, strava_id: 2))
    async def fake_update_obsidian_vault(vault_path):
        return None
    monkeypatch.setattr("src.telegram_bot.update_obsidian_vault", fake_update_obsidian_vault)

    update = FakeUpdate()
    context = SimpleNamespace(args=[])
    asyncio.run(CoachingBot.sync(update, context))

    assert any("Sincronización finalizada" in reply[0] for reply in update.message.replies)
    assert "2 actividades nuevas" in update.message.replies[-1][0]
