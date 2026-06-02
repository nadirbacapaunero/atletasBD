import logging
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os
from .mongodb_models import db, AthleteManager, ActivityManager, MetricsManager
from .strava_oauth import StravaAPIClient, StravaOAuthHandler
from .metrics import MetricsCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StravaSyncService:
    def __init__(self):
        self.athlete_manager = AthleteManager(db)
        self.activity_manager = ActivityManager(db)
        self.metrics_manager = MetricsManager(db)
        self.calculator = MetricsCalculator()
    
    def sync_all_athletes(self):
        """Sincronizar actividades de todos los atletas activos (CRON 21:00)"""
        logger.info("[SYNC] Iniciando sincronizacion Strava...")

        athletes = self.athlete_manager.get_all_active_athletes()
        logger.info(f"   Atletas a sincronizar: {len(athletes)}")

        results = {
            "total": len(athletes),
            "success": 0,
            "failed": 0,
            "new_activities": 0
        }

        for athlete in athletes:
            try:
                new_count = self.sync_athlete(athlete['_id'], athlete['strava_id'])
                results['success'] += 1
                results['new_activities'] += new_count
            except Exception as e:
                logger.error(f"[ERROR] Sincronizando {athlete['name']}: {str(e)}")
                results['failed'] += 1

        logger.info(f"[OK] Sync: {results['success']} exitosos, {results['failed']} fallos, {results['new_activities']} actividades")
        return results
    
    def _fetch_activities(self, client, last_sync):
        activities = client.get_activities(after=last_sync)
        return activities, client.last_status

    def sync_athlete(self, athlete_id, strava_id):
        """Sincronizar un atleta específico"""
        athlete = db.athletes_collection.find_one({"_id": athlete_id})
        
        if not athlete or not athlete.get('strava_access_token'):
            logger.warning(f"Atleta {athlete_id} sin token válido")
            return 0
        
        # Desencriptar token
        cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())
        try:
            access_token = cipher.decrypt(athlete['strava_access_token'].encode()).decode()
        except Exception:
            logger.error(f"Error desencriptando token para {athlete_id}")
            return 0
        
        # Crear cliente Strava
        client = StravaAPIClient(access_token)
        
        # Obtener actividades desde último sync
        last_sync = athlete.get('last_sync', datetime.utcnow() - timedelta(days=30))
        activities, status = self._fetch_activities(client, last_sync)
        
        if status == 401:
            refreshed_token = StravaOAuthHandler.refresh_access_token(strava_id)
            if refreshed_token:
                client = StravaAPIClient(refreshed_token)
                activities, status = self._fetch_activities(client, last_sync)
            else:
                logger.error(f"Error refrescando token Strava para {athlete['name']}")
                return 0
        
        if status != 200:
            logger.error(f"[ERROR] HTTP {status} al obtener actividades para {athlete['name']}")
            return 0

        if not activities:
            logger.info(f"[OK] {athlete['name']}: sin actividades nuevas")
            self.athlete_manager.update_last_sync(athlete_id)
            return 0
        
        new_count = 0
        for activity in activities:
            # Insertar actividad
            activity_id = self.activity_manager.insert_activity(athlete_id, activity)
            
            if activity_id:
                # Calcular TSS
                tss = MetricsCalculator.calculate_tss(activity, athlete.get('metadata', {}))
                
                # Actualizar TSS en BD
                db.activities_collection.update_one(
                    {"_id": activity_id},
                    {"$set": {"metrics.tss": tss}}
                )
                new_count += 1
        
        # Recalcular métricas agregadas (CTL, ATL, TSB)
        metrics = MetricsCalculator.calculate_ctl_atl_tsb(athlete_id)
        self.metrics_manager.insert_metrics(athlete_id, metrics)
        
        # Actualizar último sync
        self.athlete_manager.update_last_sync(athlete_id)

        logger.info(f"[OK] {athlete['name']}: {new_count} actividades sincronizadas")
        return new_count


# Función para ejecutar desde scheduler
async def scheduled_sync():
    """Ejecutar desde APScheduler a las 21:00"""
    service = StravaSyncService()
    service.sync_all_athletes()
