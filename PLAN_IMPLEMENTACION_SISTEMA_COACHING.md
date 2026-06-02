# PLAN IMPLEMENTACIÓN: Sistema Coaching Obsidian + MongoDB + Strava + Telegram

**Versión:** 1.0  
**Fecha:** Mayo 2026  
**Entorno:** Buenos Aires (UTC-3)  
**Sync:** 21:00 hs diarias  
**Atletas:** 30 usuarios (OAuth desde cero)

---

## 📋 TABLA DE CONTENIDOS

1. [Roadmap Implementación](#roadmap)
2. [Arquitectura Técnica](#arquitectura)
3. [Esquemas MongoDB](#schemas)
4. [Scripts Python](#scripts)
5. [Estructura Obsidian](#obsidian)
6. [Railway Deployment](#railway)
7. [Variables de Entorno](#entorno)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 ROADMAP IMPLEMENTACIÓN {#roadmap}

### **SEMANA 1: Infraestructura Base**

**Lunes-Martes: Setup Inicial**
- [ ] Crear cuenta MongoDB Atlas (FREE)
- [ ] Crear cluster + base de datos `coaching_db`
- [ ] Obtener connection string
- [ ] Crear bot Telegram (ya tenés, pero validar token)
- [ ] Crear app Strava (https://www.strava.com/settings/api)
- [ ] Obtener Strava Client ID + Client Secret

**Miércoles-Jueves: Desarrollo Local**
- [ ] Clonar repo / crear estructura de carpetas
- [ ] Instalar dependencias (requirements.txt)
- [ ] Implementar `mongodb_models.py`
- [ ] Implementar `strava_oauth.py` (OAuth flow)
- [ ] Testear OAuth localmente con 1-2 atletas

**Viernes: Primera Sincronización**
- [ ] Implementar `strava_sync.py`
- [ ] Testear descarga de actividades
- [ ] Validar datos en MongoDB

---

### **SEMANA 2: Cálculos de Métricas**

**Lunes-Martes: TSS, CTL, ATL, TSB**
- [ ] Implementar `metrics.py` (fórmulas deportivas)
- [ ] Testear cálculos con actividades reales
- [ ] Validar valores en MongoDB

**Miércoles: Escritura en Obsidian**
- [ ] Implementar `obsidian_writer.py`
- [ ] Crear templates Obsidian
- [ ] Testear generación de markdown files

**Jueves-Viernes: Telegram Bot**
- [ ] Implementar `telegram_bot.py` con Claude tool use
- [ ] Definir 5 comandos principales
- [ ] Testear respuestas del bot

---

### **SEMANA 3: Integración + Railway**

**Lunes-Martes: Orquestación Local**
- [ ] Implementar `main.py` (scheduler + coordinador)
- [ ] Testear flujo completo local (24h)
- [ ] Validar sincronía diaria a las 21:00

**Miércoles-Jueves: Railway Deployment**
- [ ] Crear cuenta Railway
- [ ] Deployer bot a Railway
- [ ] Configurar variables de entorno
- [ ] Testear sync en producción

**Viernes: Onboarding Atletas**
- [ ] Documentación OAuth para atletas
- [ ] Compartir link de autorización
- [ ] Registrar primeros atletas

---

### **SEMANA 4: Optimización + Producción**

**Lunes-Martes: Obsidian Sync**
- [ ] Configurar Obsidian Sync (opcional)
- [ ] O usar GitHub para backup
- [ ] Testear sincronía cloud

**Miércoles: Monitoreo**
- [ ] Implementar logging
- [ ] Crear alertas en Telegram si falla sync
- [ ] Dashboard básico de estado

**Jueves-Viernes: Escalabilidad**
- [ ] Documentar para los 30 atletas
- [ ] Crear plantillas de consulta para Claude
- [ ] Buffer de créditos Railway (si necesita)

---

## 🏗️ ARQUITECTURA TÉCNICA {#arquitectura}

```
┌─────────────────────────────────────────────────────────────┐
│                     FLUJO DE DATOS                          │
└─────────────────────────────────────────────────────────────┘

CAPA 1: FUENTES DE DATOS
├── Strava API (actividades de 30 atletas)
├── Telegram Bot (reportes manuales)
└── WhatsApp (opcional, webhook)

CAPA 2: PROCESAMIENTO (Railway)
├── strava_oauth.py (autorización OAuth 2.0)
├── strava_sync.py (descarga 21:00 hs)
├── metrics.py (TSS, CTL, ATL, TSB)
└── telegram_bot.py (Claude + tool use)

CAPA 3: ALMACENAMIENTO
├── MongoDB Atlas FREE (datos estructurados)
└── Obsidian Vault (markdown + queries locales)

CAPA 4: CONSULTAS/ANÁLISIS
├── Claude API (análisis avanzado vía Telegram)
├── Dataview (queries Obsidian)
└── MongoDB queries (directo)

CAPA 5: SALIDA
├── Telegram Bot (respuestas)
├── Obsidian (archivos markdown)
└── Reportes automáticos (opcional)
```

### **Stack Tecnológico**

```
Lenguaje:       Python 3.11+
Base de datos:  MongoDB Atlas (FREE)
Servidor:       Railway (FREE)
Scheduler:      APScheduler
Bot:            python-telegram-bot
API Strava:     Strava Python SDK
IA:             Claude API (tool use)
Local:          Obsidian + plugins (Dataview)
```

---

## 🗄️ ESQUEMAS MONGODB {#schemas}

### **Colección: `athletes`**

```json
{
  "_id": ObjectId,
  "strava_id": 12345678,
  "name": "Martín García",
  "email": "martin@example.com",
  "sport": "triathlon",  // triathlon, running, cycling
  "strava_access_token": "encrypted_token",
  "strava_refresh_token": "encrypted_token",
  "oauth_authorized_at": ISODate("2026-05-28T00:00:00Z"),
  "sync_status": "active",  // active, paused, deleted
  "last_sync": ISODate("2026-05-28T21:00:00Z"),
  "metadata": {
    "ftp": 280,           // Watts (cycling)
    "lthr": 165,          // Beats/min (running)
    "weight": 75,         // kg
    "max_hr": 195
  },
  "created_at": ISODate("2026-05-28T00:00:00Z"),
  "updated_at": ISODate("2026-05-28T00:00:00Z")
}
```

### **Colección: `activities`**

```json
{
  "_id": ObjectId,
  "athlete_id": ObjectId,
  "strava_activity_id": 9876543210,
  "name": "Morning Run",
  "type": "Run",  // Run, Ride, Swim, etc.
  "date": ISODate("2026-05-28T06:30:00Z"),
  "duration_seconds": 3600,
  "distance_m": 10000,
  "elevation_m": 150,
  "avg_speed_ms": 2.78,
  "avg_heart_rate": 160,
  "max_heart_rate": 178,
  "avg_cadence": 178,  // running: steps/min, cycling: rpm
  "avg_power": 0,      // cycling only (watts)
  "calories": 850,
  "temperature": 22,
  "weather_condition": "sunny",
  "perceived_effort": 8,  // 1-10 escala RPE
  "notes": "Felt strong, good pace",
  "metrics": {
    "tss": 87.5,        // Training Stress Score
    "intensity_factor": 0.92
  },
  "synced_at": ISODate("2026-05-28T21:05:00Z"),
  "created_at": ISODate("2026-05-28T21:05:00Z")
}
```

### **Colección: `metrics`**

```json
{
  "_id": ObjectId,
  "athlete_id": ObjectId,
  "date": ISODate("2026-05-28T00:00:00Z"),
  "metrics": {
    "cTL": 52.3,         // Chronic Training Load (6 weeks)
    "aTL": 38.1,         // Acute Training Load (1 week)
    "tSB": 14.2,         // Training Stress Balance
    "weekly_tss": 485,
    "monthly_tss": 1840,
    "avg_hr": 155,
    "total_distance_m": 42500,
    "total_elevation_m": 620,
    "total_calories": 5200
  },
  "sport_breakdown": {
    "running": { "tss": 280, "distance": 25000 },
    "cycling": { "tss": 205, "distance": 17500 }
  },
  "status": "recovering",  // green, yellow, red, recovering
  "updated_at": ISODate("2026-05-28T21:15:00Z")
}
```

### **Colección: `reports`**

```json
{
  "_id": ObjectId,
  "athlete_id": ObjectId,
  "date": ISODate("2026-05-28T00:00:00Z"),
  "source": "telegram",  // telegram, whatsapp, manual
  "data": {
    "lesion_areas": ["knee", "shoulder"],
    "pain_level": 4,      // 1-10
    "sleep_hours": 7.5,
    "sleep_quality": 8,   // 1-10
    "mood": 7,            // 1-10
    "stress_level": 6,    // 1-10
    "nutrition_notes": "Ate well, good hydration",
    "race_upcoming": "Marathon half-iron in 3 weeks"
  },
  "created_at": ISODate("2026-05-28T14:30:00Z")
}
```

### **Colección: `telegram_sessions`**

```json
{
  "_id": ObjectId,
  "telegram_user_id": 123456789,
  "athlete_id": ObjectId,
  "chat_id": -987654321,
  "username": "martin_grc",
  "state": "active",
  "last_message": ISODate("2026-05-28T20:15:00Z"),
  "created_at": ISODate("2026-05-28T00:00:00Z")
}
```

---

## 🐍 SCRIPTS PYTHON {#scripts}

### **1. `requirements.txt`**

```
python-telegram-bot==20.7
pymongo==4.6.1
requests==2.31.0
python-dateutil==2.8.2
APScheduler==3.10.4
python-dotenv==1.0.0
cryptography==41.0.7
anthropic==0.21.0
```

---

### **2. `config.py`** (Configuración centralizada)

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== MONGODB ====================
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "coaching_db"

# ==================== STRAVA ====================
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/callback")

# ==================== TELEGRAM ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

# ==================== CLAUDE ====================
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# ==================== OBSIDIAN ====================
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "/path/to/vault")

# ==================== SCHEDULER ====================
SYNC_TIME = "21:00"  # Buenos Aires 21:00 hs
TIMEZONE = "America/Argentina/Buenos_Aires"

# ==================== SECURITY ====================
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
```

---

### **3. `mongodb_models.py`** (Modelos + conexión)

```python
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
import os
from config import MONGODB_URI, DB_NAME

class MongoDBConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
            cls._instance.client = MongoClient(MONGODB_URI)
            cls._instance.db = cls._instance.client[DB_NAME]
            cls._instance._create_indexes()
        return cls._instance
    
    def _create_indexes(self):
        """Crear índices para optimización"""
        # Athletes
        self.db['athletes'].create_index([("strava_id", ASCENDING)], unique=True)
        self.db['athletes'].create_index([("email", ASCENDING)], unique=True)
        
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
```

---

### **4. `strava_oauth.py`** (OAuth 2.0 Strava)

```python
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta
from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI
from mongodb_models import db, AthleteManager

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_URL = "https://www.strava.com/api/v3"

athlete_manager = AthleteManager(db)


class StravaOAuthHandler:
    
    @staticmethod
    def get_authorization_url(athlete_id):
        """Generar URL de autorización para que atleta autorice en Strava"""
        params = {
            "client_id": STRAVA_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": STRAVA_REDIRECT_URI,
            "scope": "activity:read_all",
            "state": str(athlete_id)  # Usar ID del atleta como state para validar
        }
        return f"{STRAVA_AUTH_URL}?{urlencode(params)}"
    
    @staticmethod
    def exchange_code_for_token(code, state):
        """Canjear código de autorización por tokens"""
        payload = {
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(STRAVA_TOKEN_URL, data=payload)
        if response.status_code == 200:
            data = response.json()
            return {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
                "expires_at": data.get("expires_at"),
                "athlete_strava_id": data.get("athlete", {}).get("id"),
                "athlete_name": data.get("athlete", {}).get("firstname") + " " + data.get("athlete", {}).get("lastname")
            }
        return None
    
    @staticmethod
    def refresh_access_token(athlete_id):
        """Refrescar token expirado"""
        from cryptography.fernet import Fernet
        import os
        
        athlete = athlete_manager.get_athlete_by_strava_id(athlete_id)
        if not athlete:
            return None
        
        cipher = Fernet(os.getenv("ENCRYPTION_KEY").encode())
        refresh_token = cipher.decrypt(athlete['strava_refresh_token'].encode()).decode()
        
        payload = {
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        response = requests.post(STRAVA_TOKEN_URL, data=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        return None


class StravaAPIClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def get_athlete_profile(self):
        """Obtener perfil del atleta autenticado"""
        response = requests.get(
            f"{STRAVA_API_URL}/athlete",
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else None
    
    def get_activities(self, before=None, after=None, per_page=200):
        """Obtener actividades del atleta"""
        params = {
            "per_page": per_page,
            "page": 1
        }
        if before:
            params["before"] = int(before.timestamp())
        if after:
            params["after"] = int(after.timestamp())
        
        response = requests.get(
            f"{STRAVA_API_URL}/athlete/activities",
            headers=self.headers,
            params=params
        )
        return response.json() if response.status_code == 200 else []
    
    def get_activity_details(self, activity_id):
        """Obtener detalles completos de una actividad"""
        response = requests.get(
            f"{STRAVA_API_URL}/activities/{activity_id}",
            headers=self.headers
        )
        return response.json() if response.status_code == 200 else None
```

---

### **5. `metrics.py`** (Cálculos deportivos)

```python
from datetime import datetime, timedelta
from mongodb_models import db

class MetricsCalculator:
    """
    Calcula métricas de entrenamiento:
    - TSS (Training Stress Score)
    - CTL (Chronic Training Load - 6 semanas)
    - ATL (Acute Training Load - 1 semana)
    - TSB (Training Stress Balance)
    """
    
    # Factores por deporte
    SPORT_FACTORS = {
        "Run": {"ftp_equivalent": 10, "hr_multiplier": 1.0},
        "Ride": {"ftp_equivalent": 200, "hr_multiplier": 0.75},
        "Swim": {"ftp_equivalent": 8, "hr_multiplier": 1.2},
        "Walk": {"ftp_equivalent": 5, "hr_multiplier": 0.8},
    }
    
    @staticmethod
    def calculate_tss(activity_data, athlete_metadata):
        """
        TSS = (duracion_minutos * avg_hr * (avg_hr/lthr)) / (LTHR * 60) * 100
        
        Para ciclismo (si hay potencia):
        TSS = (duracion_minutos * avg_power / FTP) / 60 * 100
        """
        activity_type = activity_data.get('type', 'Run')
        duration_minutes = activity_data.get('duration_seconds', 0) / 60
        avg_hr = activity_data.get('avg_heart_rate', 0)
        avg_power = activity_data.get('avg_power', 0)
        
        if not duration_minutes:
            return 0
        
        # Ciclismo con datos de potencia
        if activity_type == "Ride" and avg_power:
            ftp = athlete_metadata.get('ftp', 200)
            if ftp and avg_power:
                intensity_factor = avg_power / ftp
                tss = (duration_minutes * avg_power / ftp / 60) * 100
                return round(tss, 1)
        
        # Running/Nadadores con HR
        if avg_hr:
            lthr = athlete_metadata.get('lthr', 160)
            if lthr:
                intensity_factor = avg_hr / lthr
                tss = (duration_minutes * intensity_factor * intensity_factor) / 60 * 100
                return round(tss, 1)
        
        # Fallback: por duración (en ausencia de HR/Power)
        return round(duration_minutes * 0.8, 1)
    
    @staticmethod
    def calculate_ctl_atl_tsb(athlete_id, days=42):
        """
        CTL: Chronic Training Load (promedio últimas 6 semanas con decay)
        ATL: Acute Training Load (promedio última semana con decay)
        TSB: Training Stress Balance (CTL - ATL)
        
        Usa fórmula exponencial móvil con constantes de decay
        """
        from mongodb_models import ActivityManager
        
        activity_manager = ActivityManager(db)
        activities = activity_manager.get_activities_by_athlete(athlete_id, days=days)
        
        if not activities:
            return {"cTL": 0, "aTL": 0, "tSB": 0}
        
        # Decay constants
        ctl_decay = 42  # 6 semanas
        atl_decay = 7   # 1 semana
        
        # Calcular CTL y ATL con promedio móvil exponencial
        ctl = 0
        atl = 0
        
        for activity in reversed(activities):  # Desde más antiguo a más nuevo
            tss = activity.get('metrics', {}).get('tss', 0)
            days_ago = (datetime.utcnow() - activity.get('date')).days
            
            # Fórmula exponencial
            ctl = tss + ctl * (1 - 1/ctl_decay)
            if days_ago <= 7:
                atl = tss + atl * (1 - 1/atl_decay)
        
        tsb = ctl - atl
        
        return {
            "cTL": round(ctl, 1),
            "aTL": round(atl, 1),
            "tSB": round(tsb, 1),
            "weekly_tss": round(atl, 1),
            "status": MetricsCalculator.get_training_status(ctl, atl, tsb)
        }
    
    @staticmethod
    def get_training_status(ctl, atl, tsb):
        """Determinar estado de entrenamiento"""
        if tsb > 25:
            return "overreaching"  # Rojo - Sobreentrenamiento
        elif tsb > 5:
            return "peak"  # Verde - Mejor rendimiento
        elif tsb > -10:
            return "training"  # Amarillo - En entrenamiento
        else:
            return "fatigued"  # Rojo - Fatigado
    
    @staticmethod
    def generate_weekly_summary(athlete_id):
        """Generar resumen semanal con todas las métricas"""
        from mongodb_models import ActivityManager
        
        activity_manager = ActivityManager(db)
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        activities = list(db.activities_collection.find({
            "athlete_id": athlete_id,
            "date": {"$gte": week_ago}
        }))
        
        summary = {
            "activities_count": len(activities),
            "total_distance": round(sum(a.get('distance_m', 0) for a in activities) / 1000, 1),
            "total_tss": round(sum(a.get('metrics', {}).get('tss', 0) for a in activities), 1),
            "total_elevation": round(sum(a.get('elevation_m', 0) for a in activities), 0),
            "avg_hr": round(sum(a.get('avg_heart_rate', 0) for a in activities if a.get('avg_heart_rate')) / len([a for a in activities if a.get('avg_heart_rate')]), 0) if any(a.get('avg_heart_rate') for a in activities) else 0,
            "disciplines": {}
        }
        
        # Desglose por disciplina
        for activity in activities:
            sport = activity.get('type', 'Other')
            if sport not in summary['disciplines']:
                summary['disciplines'][sport] = {
                    "count": 0,
                    "distance": 0,
                    "tss": 0
                }
            summary['disciplines'][sport]['count'] += 1
            summary['disciplines'][sport]['distance'] += activity.get('distance_m', 0) / 1000
            summary['disciplines'][sport]['tss'] += activity.get('metrics', {}).get('tss', 0)
        
        return summary
```

---

### **6. `strava_sync.py`** (Descarga y sincronización)

```python
import logging
from datetime import datetime, timedelta
from cryptography.fernet import Cipher, Fernet
import os
from mongodb_models import db, AthleteManager, ActivityManager, MetricsManager
from strava_oauth import StravaAPIClient, StravaOAuthHandler
from metrics import MetricsCalculator

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
        logger.info("🔄 Iniciando sync Strava para todos los atletas...")
        
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
                logger.error(f"❌ Error sincronizando {athlete['name']}: {str(e)}")
                results['failed'] += 1
        
        logger.info(f"✅ Sync completado: {results['success']} exitosos, {results['failed']} fallos, {results['new_activities']} actividades nuevas")
        return results
    
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
        except:
            logger.error(f"Error desencriptando token para {athlete_id}")
            return 0
        
        # Crear cliente Strava
        client = StravaAPIClient(access_token)
        
        # Obtener actividades desde último sync
        last_sync = athlete.get('last_sync', datetime.utcnow() - timedelta(days=30))
        activities = client.get_activities(after=last_sync)
        
        if not activities:
            logger.info(f"✓ {athlete['name']}: sin actividades nuevas")
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
        
        logger.info(f"✓ {athlete['name']}: {new_count} actividades sincronizadas")
        return new_count


# Función para ejecutar desde scheduler
async def scheduled_sync():
    """Ejecutar desde APScheduler a las 21:00"""
    service = StravaSyncService()
    service.sync_all_athletes()
```

---

### **7. `telegram_bot.py`** (Bot con Claude tool use)

```python
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, CLAUDE_API_KEY
from mongodb_models import db, AthleteManager
from strava_oauth import StravaOAuthHandler
from anthropic import Anthropic
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar cliente Anthropic
client_anthropic = Anthropic(api_key=CLAUDE_API_KEY)
athlete_manager = AthleteManager(db)

class CoachingBot:
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user
        chat_id = update.message.chat_id
        
        text = f"""
🏃 **Bienvenido a tu Coach AI** {user.first_name}!

Soy tu asistente personal de entrenamiento. Aquí puedes:

**Comandos principales:**
/register - Conectar tu cuenta Strava
/status - Ver tu estado de entrenamiento actual
/weekly - Resumen semanal
/ask - Preguntarme sobre tu entrenamiento
/help - Ayuda

¿Comenzamos?
        """
        await update.message.reply_text(text, parse_mode="Markdown")
    
    @staticmethod
    async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /register - Iniciar OAuth con Strava"""
        user = update.effective_user
        chat_id = update.message.chat_id
        
        # Crear sesión Telegram
        db.sessions_collection.update_one(
            {"telegram_user_id": user.id},
            {
                "$set": {
                    "telegram_user_id": user.id,
                    "chat_id": chat_id,
                    "username": user.username,
                    "state": "awaiting_strava_auth"
                }
            },
            upsert=True
        )
        
        # Enviar link de autorización
        auth_url = StravaOAuthHandler.get_authorization_url(user.id)
        
        text = f"""
🔗 **Conecta tu cuenta Strava**

Haz click en el botón abajo para autorizar el acceso a tus actividades:

[Autorizar con Strava]({auth_url})

Una vez autorizado, pueda sincronizaré automáticamente tus entrenamientos cada noche a las 21:00.
        """
        
        await update.message.reply_text(text, parse_mode="Markdown")
    
    @staticmethod
    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Estado de entrenamiento actual"""
        user = update.effective_user
        
        # Buscar atleta por sesión Telegram
        session = db.sessions_collection.find_one({"telegram_user_id": user.id})
        if not session or not session.get('athlete_id'):
            await update.message.reply_text("❌ Primero debes conectar tu cuenta Strava con /register")
            return
        
        # Obtener métricas
        metrics = db.metrics_collection.find_one(
            {"athlete_id": session['athlete_id']},
            sort=[("date", -1)]
        )
        
        if not metrics:
            await update.message.reply_text("⏳ Aún no hay datos. Espera al próximo sync (21:00).")
            return
        
        m = metrics['metrics']
        status_emoji = {
            "overreaching": "🔴",
            "peak": "🟢",
            "training": "🟡",
            "fatigued": "🔴"
        }.get(m.get('status'), "⚪")
        
        text = f"""
{status_emoji} **Tu Estado Actual**

**Cargas de Entrenamiento:**
• CTL (Carga Crónica): {m.get('cTL', 0)} TSS
• ATL (Carga Aguda): {m.get('aTL', 0)} TSS
• TSB (Balance): {m.get('tSB', 0)} TSS

**Esta Semana:**
• TSS Total: {m.get('weekly_tss', 0)}
• Distancia: {m.get('total_distance_m', 0)/1000:.1f} km

**Estado:** {m.get('status', 'unknown')}
        """
        
        await update.message.reply_text(text, parse_mode="Markdown")
    
    @staticmethod
    async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ask - Consultar a Claude AI sobre entrenamientos"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("📝 Uso: /ask [tu pregunta]")
            return
        
        question = " ".join(context.args)
        
        # Buscar atleta
        session = db.sessions_collection.find_one({"telegram_user_id": user.id})
        if not session or not session.get('athlete_id'):
            await update.message.reply_text("❌ Primero conecta con /register")
            return
        
        athlete_id = session['athlete_id']
        
        # Obtener datos del atleta para contexto
        athlete = db.athletes_collection.find_one({"_id": athlete_id})
        metrics = db.metrics_collection.find_one(
            {"athlete_id": athlete_id},
            sort=[("date", -1)]
        )
        
        # Construir contexto para Claude
        context_data = {
            "athlete": athlete['name'],
            "sport": athlete.get('sport', 'triathlon'),
            "current_metrics": metrics.get('metrics', {}) if metrics else {},
            "recent_activities": list(db.activities_collection.find(
                {"athlete_id": athlete_id},
                sort=[("date", -1)],
                limit=5
            ))
        }
        
        # Llamar Claude con tool use
        system_prompt = f"""
Eres un coach de triatlón experto. Tienes datos de entrenamiento de {athlete['name']}.

Datos actuales:
{json.dumps(context_data, default=str, indent=2)}

Responde en español, de manera concisa (máximo 3-4 párrafos).
Si mencionas valores numéricos, sé específico con unidades.
"""
        
        try:
            response = client_anthropic.messages.create(
                model="claude-opus-4-20250805",
                max_tokens=500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question}
                ]
            )
            
            answer = response.content[0].text
            await update.message.reply_text(answer, parse_mode="Markdown")
        
        except Exception as e:
            logger.error(f"Error en Claude: {str(e)}")
            await update.message.reply_text(f"❌ Error procesando tu pregunta: {str(e)}")
    
    @staticmethod
    async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /weekly - Resumen semanal"""
        user = update.effective_user
        
        session = db.sessions_collection.find_one({"telegram_user_id": user.id})
        if not session or not session.get('athlete_id'):
            await update.message.reply_text("❌ Conecta con /register primero")
            return
        
        from metrics import MetricsCalculator
        
        summary = MetricsCalculator.generate_weekly_summary(session['athlete_id'])
        
        text = f"""
📊 **Resumen Semanal**

**Volumen:**
• Actividades: {summary['activities_count']}
• Distancia: {summary['total_distance']:.1f} km
• TSS Total: {summary['total_tss']:.0f}
• Desnivel: {summary['total_elevation']:.0f} m

**Por Disciplina:**
"""
        
        for sport, data in summary['disciplines'].items():
            text += f"\n**{sport}:**\n  • {data['count']} sesiones\n  • {data['distance']:.1f} km\n  • {data['tss']:.0f} TSS"
        
        await update.message.reply_text(text, parse_mode="Markdown")


# Inicializar aplicación Telegram
def create_app():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", CoachingBot.start))
    app.add_handler(CommandHandler("register", CoachingBot.register))
    app.add_handler(CommandHandler("status", CoachingBot.status))
    app.add_handler(CommandHandler("weekly", CoachingBot.weekly))
    app.add_handler(CommandHandler("ask", CoachingBot.ask))
    
    return app


# Para ejecutar
if __name__ == "__main__":
    app = create_app()
    app.run_polling()
```

---

### **8. `obsidian_writer.py`** (Generador de markdown)

```python
import os
from datetime import datetime
from pathlib import Path
from mongodb_models import db
import json

class ObsidianVaultWriter:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.athletes_folder = self.vault_path / "Atletas"
        self.activities_folder = self.vault_path / "Actividades"
        self.metrics_folder = self.vault_path / "Métricas"
        
        # Crear carpetas si no existen
        self.athletes_folder.mkdir(parents=True, exist_ok=True)
        self.activities_folder.mkdir(parents=True, exist_ok=True)
        self.metrics_folder.mkdir(parents=True, exist_ok=True)
    
    def generate_athlete_profile(self, athlete_id, athlete_data):
        """Generar perfil del atleta en Obsidian"""
        athlete_name = athlete_data['name'].replace(" ", "_")
        filepath = self.athletes_folder / f"{athlete_name}.md"
        
        content = f"""# {athlete_data['name']}

**ID Strava:** {athlete_data['strava_id']}
**Deporte:** {athlete_data.get('sport', 'Triatlón')}
**Estado Sync:** {athlete_data.get('sync_status', 'pending')}
**Último Sync:** {athlete_data.get('last_sync', 'N/A')}

## Datos Personales

| Campo | Valor |
|-------|-------|
| FTP (W) | {athlete_data.get('metadata', {}).get('ftp', 'N/A')} |
| LTHR (bpm) | {athlete_data.get('metadata', {}).get('lthr', 'N/A')} |
| Peso (kg) | {athlete_data.get('metadata', {}).get('weight', 'N/A')} |
| FC Máx | {athlete_data.get('metadata', {}).get('max_hr', 'N/A')} |

## Actividades Recientes

```dataview
list
from "Actividades"
where athlete = "{athlete_name}"
sort date descending
limit 10
```

## Métricas

```dataview
table cTL, aTL, tSB
from "Métricas"
where athlete = "{athlete_name}"
sort date descending
limit 5
```

## Reportes

```dataview
list
from "Reportes"
where athlete = "{athlete_name}"
sort date descending
```
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_activity_note(self, activity_data):
        """Generar nota de actividad individual"""
        date_str = activity_data['date'].strftime("%Y-%m-%d %H:%M")
        filename = f"{date_str}_{activity_data['name'].replace(' ', '_')}.md"
        filepath = self.activities_folder / filename
        
        athlete = db.athletes_collection.find_one({"_id": activity_data['athlete_id']})
        
        content = f"""# {activity_data['name']}

**Atleta:** [[{athlete['name']}]]
**Tipo:** {activity_data['type']}
**Fecha:** {date_str}

## Resumen

| Métrica | Valor |
|---------|-------|
| Distancia | {activity_data.get('distance_m', 0)/1000:.2f} km |
| Tiempo | {activity_data.get('duration_seconds', 0)//60} min |
| Velocidad Promedio | {activity_data.get('avg_speed_ms', 0)*3.6:.2f} km/h |
| FC Promedio | {activity_data.get('avg_heart_rate', 'N/A')} bpm |
| FC Máxima | {activity_data.get('max_heart_rate', 'N/A')} bpm |
| Desnivel | {activity_data.get('elevation_m', 0):.0f} m |
| TSS | {activity_data.get('metrics', {}).get('tss', 'N/A')} |

## Notas

{activity_data.get('notes', 'Sin notas')}

## Tags

#actividad #{activity_data['type']} #{athlete['name'].replace(' ', '')}
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_daily_metrics(self, athlete_id, athlete_name, metrics_data):
        """Generar nota diaria de métricas"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"{athlete_name.replace(' ', '_')}_{today}_Metrics.md"
        filepath = self.metrics_folder / filename
        
        m = metrics_data['metrics']
        
        content = f"""# Métricas de {athlete_name} - {today}

**Fecha:** {today}
**Atleta:** [[{athlete_name}]]

## Cargas de Entrenamiento

| Métrica | Valor | Interpretación |
|---------|-------|-----------------|
| **CTL** | {m.get('cTL', 0)} | Carga crónica (6 semanas) |
| **ATL** | {m.get('aTL', 0)} | Carga aguda (1 semana) |
| **TSB** | {m.get('tSB', 0)} | Balance de estrés |
| **Estado** | {m.get('status', 'unknown')} | Recomendación |

## Resumen Semanal

- **TSS Total:** {m.get('weekly_tss', 0)}
- **Distancia:** {m.get('total_distance_m', 0)/1000:.1f} km
- **Desnivel:** {m.get('total_elevation_m', 0):.0f} m
- **FC Promedio:** {m.get('avg_hr', 'N/A')} bpm

### Por Disciplina
"""
        
        for sport, data in m.get('sport_breakdown', {}).items():
            content += f"\n- **{sport}**: {data.get('tss', 0)} TSS, {data.get('distance', 0)/1000:.1f} km"
        
        content += f"\n\n## Recomendaciones\n\n"
        
        status = m.get('status', 'unknown')
        if status == "peak":
            content += "🟢 **ÓPTIMO PARA COMPETENCIA** - Estás en tu mejor momento. Considera competencias de alto nivel."
        elif status == "training":
            content += "🟡 **EN ENTRENAMIENTO** - Continúa con la acumulación. Buena ventana para entrenamientos duros."
        elif status == "fatigued":
            content += "🔴 **FATIGADO** - Necesitas recuperación. Reduce volumen o intensidad."
        elif status == "overreaching":
            content += "🔴 **SOBRENTRENADO** - Riesgo de lesión. Descansa mínimo 2-3 días."
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_index(self):
        """Generar índice general del vault"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        filepath = self.vault_path / "INDEX.md"
        
        # Obtener todos los atletas
        athletes = list(db.athletes_collection.find({"sync_status": "active"}))
        
        content = f"""# 🏃 Sistema de Coaching - Índice

**Actualizado:** {today}
**Total de Atletas:** {len(athletes)}

## 📋 Atletas

| Nombre | Deporte | Estado | Último Sync |
|--------|---------|--------|------------|
"""
        
        for athlete in athletes:
            name = athlete['name']
            sport = athlete.get('sport', 'Triatlón')
            status = athlete.get('sync_status', 'N/A')
            last_sync = athlete.get('last_sync', 'Nunca').strftime("%d/%m %H:%M") if athlete.get('last_sync') else 'Nunca'
            content += f"| [[{name}]] | {sport} | {status} | {last_sync} |\n"
        
        content += f"""

## 📊 Carpetas

- **Atletas/** - Perfiles individuales
- **Actividades/** - Entrenamientos importados desde Strava
- **Métricas/** - Cálculos CTL/ATL/TSB diarios
- **Reportes/** - Reportes manuales de lesiones, sueño, etc.

## 🔗 Queries Útiles

### Atletas con Fatiga
\`\`\`dataview
list
from "Atletas"
where status = "fatigued"
\`\`\`

### Actividades Esta Semana
\`\`\`dataview
list
from "Actividades"
where date >= today - 7
sort date descending
\`\`\`

### Top 5 Sesiones por TSS
\`\`\`dataview
table name, type, tss
from "Actividades"
sort tss descending
limit 5
\`\`\`
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


# Función para actualizar Obsidian después de sync
async def update_obsidian_vault(vault_path):
    """Llamar después de cada sync para actualizar Obsidian"""
    writer = ObsidianVaultWriter(vault_path)
    
    # Actualizar todos los atletas
    athletes = db.athletes_collection.find({"sync_status": "active"})
    for athlete in athletes:
        writer.generate_athlete_profile(athlete['_id'], athlete)
        
        # Actualizar actividades recientes
        activities = db.activities_collection.find(
            {"athlete_id": athlete['_id']},
            sort=[("date", -1)],
            limit=20
        )
        for activity in activities:
            writer.generate_activity_note(activity)
        
        # Actualizar métricas
        metrics = db.metrics_collection.find_one(
            {"athlete_id": athlete['_id']},
            sort=[("date", -1)]
        )
        if metrics:
            writer.generate_daily_metrics(athlete['_id'], athlete['name'], metrics)
    
    # Regenerar índice
    writer.generate_index()
```

---

### **9. `main.py`** (Orquestador + Scheduler)

```python
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application
from config import SYNC_TIME, TIMEZONE, TELEGRAM_BOT_TOKEN, OBSIDIAN_VAULT_PATH
from strava_sync import StravaSyncService
from telegram_bot import CoachingBot, create_app
from obsidian_writer import update_obsidian_vault

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoachingSystem:
    def __init__(self):
        self.sync_service = StravaSyncService()
        self.scheduler = None
        self.app = None
    
    async def scheduled_sync_task(self):
        """Tarea que se ejecuta a las 21:00 hs Buenos Aires"""
        logger.info("=" * 50)
        logger.info("🔄 INICIANDO SINCRONIZACIÓN PROGRAMADA")
        logger.info("=" * 50)
        
        try:
            # 1. Sincronizar Strava
            results = self.sync_service.sync_all_athletes()
            
            # 2. Actualizar Obsidian
            await update_obsidian_vault(OBSIDIAN_VAULT_PATH)
            
            # 3. Notificar al admin (opcional)
            logger.info(f"✅ Sync completado: {results}")
            
        except Exception as e:
            logger.error(f"❌ Error en sync: {str(e)}", exc_info=True)
    
    async def start(self):
        """Iniciar el sistema"""
        logger.info("🚀 Iniciando Sistema de Coaching...")
        
        # Crear scheduler
        self.scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        
        # Programar sync diario
        hour, minute = SYNC_TIME.split(':')
        self.scheduler.add_job(
            self.scheduled_sync_task,
            CronTrigger(hour=int(hour), minute=int(minute), timezone=TIMEZONE),
            id='strava_sync_job',
            name='Strava Sync Diario 21:00 hs'
        )
        
        self.scheduler.start()
        logger.info(f"⏰ Scheduler iniciado. Sync programado para {SYNC_TIME} hs")
        
        # Iniciar bot Telegram
        self.app = create_app()
        logger.info("🤖 Bot Telegram iniciado")
        
        # Ejecutar en paralelo
        await self.app.run_polling()
    
    async def stop(self):
        """Detener el sistema"""
        if self.scheduler:
            self.scheduler.shutdown()
        if self.app:
            await self.app.stop()


async def main():
    system = CoachingSystem()
    
    try:
        await system.start()
    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo sistema...")
        await system.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📁 ESTRUCTURA OBSIDIAN {#obsidian}

### **Carpetas principales:**

```
Vault/
├── Atletas/
│   ├── Martin_Garcia.md
│   ├── Pablo_Mendez.md
│   └── ... (30 atletas)
│
├── Actividades/
│   ├── 2026-05-28_10-30_Morning_Run.md
│   ├── 2026-05-28_17-00_Bike_Session.md
│   └── ... (histórico de entrenamientos)
│
├── Métricas/
│   ├── Martin_Garcia_2026-05-28_Metrics.md
│   ├── Pablo_Mendez_2026-05-28_Metrics.md
│   └── ... (diarias)
│
├── Reportes/
│   ├── 2026-05-28_Lesiones.md
│   ├── 2026-05-28_Sueño.md
│   └── ... (reportes manuales)
│
├── Templates/
│   ├── Athlete_Profile.md
│   ├── Activity.md
│   ├── Daily_Metrics.md
│   └── Manual_Report.md
│
├── Queries/
│   ├── Fatiga_Actual.md
│   ├── Top_Performances.md
│   └── Weekly_Summary.md
│
└── INDEX.md
```

### **Plugin Configuration:**

```json
{
  "plugins": {
    "dataview": {
      "enableDataviewJs": true,
      "enableInlineDataview": true
    },
    "obsidian-git": {
      "autoCommitMessage": "Sync Coaching Data",
      "autoPushInterval": 5
    }
  }
}
```

---

## 🚀 RAILWAY DEPLOYMENT {#railway}

### **Paso 1: Crear cuenta Railway**

1. Ir a https://railway.app
2. Crear proyecto nuevo
3. Conectar repositorio GitHub

### **Paso 2: Variables de entorno en Railway**

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/coaching_db
STRAVA_CLIENT_ID=xxx
STRAVA_CLIENT_SECRET=xxx
STRAVA_REDIRECT_URI=https://tu-bot.railway.app/callback
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_ADMIN_ID=xxx
CLAUDE_API_KEY=xxx
ENCRYPTION_KEY=xxx
OBSIDIAN_VAULT_PATH=/tmp/vault
```

### **Paso 3: Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### **Paso 4: Deploy**

```bash
# En tu repo local
git add .
git commit -m "Deploy coaching system"
git push

# Railway detecta cambios y redeploy automático
```

---

## ⚙️ VARIABLES DE ENTORNO {#entorno}

### **`.env` (local)**

```bash
# MONGODB
MONGODB_URI=mongodb+srv://user:password@cluster-xxx.mongodb.net/coaching_db?retryWrites=true&w=majority

# STRAVA
STRAVA_CLIENT_ID=123456
STRAVA_CLIENT_SECRET=abc123def456
STRAVA_REDIRECT_URI=http://localhost:8000/callback

# TELEGRAM
TELEGRAM_BOT_TOKEN=123456:ABCDefGhIjKlMnOpQrStUvWxYz
TELEGRAM_ADMIN_ID=987654321

# CLAUDE
CLAUDE_API_KEY=sk-ant-xxx

# OBSIDIAN
OBSIDIAN_VAULT_PATH=/Users/tu_usuario/Library/Mobile\ Documents/iCloud\~md\~obsidian/Documents/tu_vault

# ENCRYPTION
ENCRYPTION_KEY=bVN5R2s...  # Generar: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"
```

---

## 🔧 TROUBLESHOOTING {#troubleshooting}

### **Error: "MONGODB_URI invalid"**
```bash
# Verificar string de conexión
# Incluir usuario:password (URL-encoded)
# Permitir IP 0.0.0.0 en MongoDB Atlas
```

### **Error: "Strava token expired"**
```
El bot intenta refrescar automáticamente.
Si sigue fallando, hacer que atleta se reautentifique con /register
```

### **Obsidian no se actualiza**
```
- Verificar OBSIDIAN_VAULT_PATH existe
- Dar permisos de escritura al directorio
- Asegurar que Obsidian está cerrado durante escritura
```

### **Sync no ejecuta a las 21:00**
```bash
# Verificar timezone en config.py
# En Railway: TZ=America/Argentina/Buenos_Aires
# Revisar logs: railway logs [project-id]
```

### **Claude API error**
```
- Validar CLAUDE_API_KEY válida
- Verificar créditos disponibles
- Revisar límites de rate limit
```

---

## 📝 PRÓXIMOS PASOS

1. **Semana 1:** Configurar MongoDB + Strava OAuth
2. **Semana 2:** Implementar métricas + bot local
3. **Semana 3:** Deploy a Railway + onboarding atletas
4. **Semana 4:** Optimización + escalabilidad

¡Adelante con Claude Code! 🚀

---

**Última actualización:** 2026-05-28  
**Versión:** 1.0  
**Estado:** Listo para implementar
