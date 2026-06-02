from datetime import datetime, timedelta
from .mongodb_models import db

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
            lthr = athlete_metadata.get('lthr', 150)
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
        from .mongodb_models import ActivityManager
        
        activity_manager = ActivityManager(db)
        activities = activity_manager.get_activities_by_athlete(athlete_id, days=days)
        
        if not activities:
            return {"cTL": 0, "aTL": 0, "tSB": 0, "weekly_tss": 0, "status": "recovering"}
        
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
        from .mongodb_models import ActivityManager
        
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
