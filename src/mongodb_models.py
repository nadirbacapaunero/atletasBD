from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
import os
from .config import MONGODB_URI, DB_NAME

class MongoDBConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
            cls._instance.client = None
            cls._instance._db = None
        return cls._instance
    
    def _ensure_connection(self):
        if self.client is None:
            if not MONGODB_URI:
                raise RuntimeError("MONGODB_URI is not configured")
            self.client = MongoClient(MONGODB_URI)
            self._db = self.client[DB_NAME]
            self._create_indexes()
    
    @property
    def db(self):
        self._ensure_connection()
        return self._db
    
    def _create_indexes(self):
        """Crear índices para optimización"""
        # Athletes
        self._db['athletes'].create_index([("strava_id", ASCENDING)], unique=True)
        self._db['athletes'].create_index([("email", ASCENDING)], unique=True)
        
        # Activities
        self.db['activities'].create_index([("athlete_id", ASCENDING), ("date", DESCENDING)])
        self.db['activities'].create_index([("strava_activity_id", ASCENDING)], unique=True)
        
        # Metrics
        self.db['metrics'].create_index([("athlete_id", ASCENDING), ("date", DESCENDING)])
        
        # Reports
        self.db['reports'].create_index([("athlete_id", ASCENDING), ("date", DESCENDING)])
        
        # Sessions
        self.db['telegram_sessions'].create_index([("telegram_user_id", ASCENDING)], unique=True)

    @property
    def athletes_collection(self):
        return self.db['athletes']
    
    @property
    def activities_collection(self):
        return self.db['activities']
    
    @property
    def metrics_collection(self):
        return self.db['metrics']
    
    @property
    def reports_collection(self):
        return self.db['reports']
    
    @property
    def sessions_collection(self):
        return self.db['telegram_sessions']


class AthleteManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_athlete(self, strava_id, name, email, sport="triathlon"):
        """Crear nuevo atleta"""
        athlete = {
            "strava_id": strava_id,
            "name": name,
            "email": email,
            "sport": sport,
            "strava_access_token": None,
            "strava_refresh_token": None,
            "oauth_authorized_at": None,
            "sync_status": "pending",
            "last_sync": None,
            "metadata": {
                "ftp": None,
                "lthr": None,
                "weight": None,
                "max_hr": None
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        try:
            result = self.db.athletes_collection.insert_one(athlete)
            return result.inserted_id
        except DuplicateKeyError:
            return None
    
    def get_athlete_by_strava_id(self, strava_id):
        """Obtener atleta por ID Strava"""
        return self.db.athletes_collection.find_one({"strava_id": strava_id})
    
    def get_all_active_athletes(self):
        """Obtener todos los atletas activos"""
        return list(self.db.athletes_collection.find({"sync_status": "active"}))
    
    def update_athlete_tokens(self, athlete_id, access_token, refresh_token):
        """Actualizar tokens OAuth después de autorizar"""
        from cryptography.fernet import Fernet
        cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())
        
        encrypted_access = cipher.encrypt(access_token.encode()).decode()
        encrypted_refresh = cipher.encrypt(refresh_token.encode()).decode()
        
        self.db.athletes_collection.update_one(
            {"_id": athlete_id},
            {
                "$set": {
                    "strava_access_token": encrypted_access,
                    "strava_refresh_token": encrypted_refresh,
                    "oauth_authorized_at": datetime.utcnow(),
                    "sync_status": "active",
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    def update_last_sync(self, athlete_id):
        """Registrar último sync"""
        self.db.athletes_collection.update_one(
            {"_id": athlete_id},
            {"$set": {"last_sync": datetime.utcnow()}}
        )


class ActivityManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def insert_activity(self, athlete_id, strava_activity):
        """Insertar actividad desde Strava"""
        activity = {
            "athlete_id": athlete_id,
            "strava_activity_id": strava_activity['id'],
            "name": strava_activity.get('name'),
            "type": strava_activity.get('type'),
            "date": strava_activity.get('start_date_local'),
            "duration_seconds": strava_activity.get('elapsed_time'),
            "distance_m": strava_activity.get('distance'),
            "elevation_m": strava_activity.get('total_elevation_gain'),
            "avg_speed_ms": strava_activity.get('average_speed'),
            "avg_heart_rate": strava_activity.get('average_heartrate'),
            "max_heart_rate": strava_activity.get('max_heartrate'),
            "avg_cadence": strava_activity.get('average_cadence'),
            "avg_power": strava_activity.get('average_watts'),
            "calories": strava_activity.get('kilojoules') * 4.184 if strava_activity.get('kilojoules') else 0,
            "perceived_effort": None,
            "notes": strava_activity.get('description'),
            "metrics": {
                "tss": None,  # Se calcula después
                "intensity_factor": None
            },
            "synced_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        try:
            result = self.db.activities_collection.insert_one(activity)
            return result.inserted_id
        except DuplicateKeyError:
            return None
    
    def get_activities_by_athlete(self, athlete_id, days=30):
        """Obtener actividades de un atleta (últimos X días)"""
        since = datetime.utcnow() - timedelta(days=days)
        return list(
            self.db.activities_collection.find(
                {"athlete_id": athlete_id, "date": {"$gte": since}}
            ).sort("date", DESCENDING)
        )


class MetricsManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def insert_metrics(self, athlete_id, metrics_data):
        """Insertar métricas calculadas del día"""
        metrics = {
            "athlete_id": athlete_id,
            "date": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            "metrics": metrics_data,
            "updated_at": datetime.utcnow()
        }
        
        self.db.metrics_collection.update_one(
            {"athlete_id": athlete_id, "date": metrics['date']},
            {"$set": metrics},
            upsert=True
        )
    
    def get_latest_metrics(self, athlete_id):
        """Obtener última métrica registrada"""
        return self.db.metrics_collection.find_one(
            {"athlete_id": athlete_id},
            sort=[("date", DESCENDING)]
        )


# Inicializar conexión
db = MongoDBConnection()
