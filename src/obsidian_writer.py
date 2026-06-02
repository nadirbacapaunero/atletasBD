import os
from datetime import datetime
from pathlib import Path
from .mongodb_models import db
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
```dataview
list
from "Atletas"
where status = "fatigued"
```

### Actividades Esta Semana
```dataview
list
from "Actividades"
where date >= today - 7
sort date descending
```

### Top 5 Sesiones por TSS
```dataview
table name, type, tss
from "Actividades"
sort tss descending
limit 5
```
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
