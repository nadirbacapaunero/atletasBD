import asyncio
from types import SimpleNamespace

from src.main import CoachingSystem


def test_scheduled_sync_sends_admin_message(monkeypatch):
    fake_calls = []

    class FakeBot:
        async def send_message(self, chat_id, text):
            fake_calls.append((chat_id, text))

    fake_app = SimpleNamespace(bot=FakeBot())
    fake_service = SimpleNamespace(sync_all_athletes=lambda: {
        "success": 2,
        "failed": 0,
        "new_activities": 5
    })

    system = CoachingSystem()
    system.sync_service = fake_service
    system.app = fake_app

    monkeypatch.setattr("src.main.TELEGRAM_ADMIN_ID", 555)
    async def fake_update_obsidian_vault(vault_path):
        return None
    monkeypatch.setattr("src.main.update_obsidian_vault", fake_update_obsidian_vault)

    asyncio.run(system.scheduled_sync_task())

    assert fake_calls == [
        (555, "✅ Sync completado: 2 exitosos, 0 fallos, 5 actividades nuevas")
    ]
