import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application
from .config import SYNC_TIME, TIMEZONE, TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_ID, OBSIDIAN_VAULT_PATH
from .strava_sync import StravaSyncService
from .telegram_bot import CoachingBot, create_app
from .obsidian_writer import update_obsidian_vault

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoachingSystem:
    def __init__(self):
        self.sync_service = StravaSyncService()
        self.scheduler = None
        self.app = None

    def scheduled_sync_task(self):
        """Tarea que se ejecuta a las 21:00 hs Buenos Aires"""
        logger.info("=" * 50)
        logger.info("[SYNC] Iniciando sincronizacion programada")
        logger.info("=" * 50)

        try:
            # 1. Sincronizar Strava
            results = self.sync_service.sync_all_athletes()

            # 2. Actualizar Obsidian (ejecutar async dentro del scheduler)
            asyncio.run(update_obsidian_vault(OBSIDIAN_VAULT_PATH))

            summary = (
                f"[OK] Sync completado: {results['success']} exitosos, "
                f"{results['failed']} fallos, {results['new_activities']} actividades nuevas"
            )

            # 3. Log (notificación Telegram requiere event loop del bot, se omite del scheduler)
            logger.info(summary)

        except Exception as e:
            error_text = f"[ERROR] Sync programado: {str(e)}"
            logger.error(error_text, exc_info=True)

    def start(self):
        """Iniciar el sistema"""
        logger.info("[START] Iniciando Sistema de Coaching...")

        # Crear scheduler (BackgroundScheduler corre en thread separado)
        self.scheduler = BackgroundScheduler(timezone=TIMEZONE)

        # Programar sync diario
        hour, minute = SYNC_TIME.split(':')
        self.scheduler.add_job(
            self.scheduled_sync_task,
            CronTrigger(hour=int(hour), minute=int(minute), timezone=TIMEZONE),
            id='strava_sync_job',
            name='Strava Sync Diario 21:00 hs'
        )

        self.scheduler.start()
        logger.info(f"[SCHEDULER] Iniciado. Sync programado para {SYNC_TIME} hs")

        # Iniciar bot Telegram
        self.app = create_app()
        logger.info("[BOT] Telegram iniciado")

        # Ejecutar bot (run_polling bloquea pero en main thread)
        self.app.run_polling()

    def stop(self):
        """Detener el sistema"""
        if self.scheduler:
            self.scheduler.shutdown()


def main():
    system = CoachingSystem()

    try:
        system.start()
    except KeyboardInterrupt:
        logger.info("\n[STOP] Deteniendo sistema...")
        system.stop()


if __name__ == "__main__":
    main()
