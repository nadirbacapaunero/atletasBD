# 🏃 Sistema de Coaching - Índice

**Actualizado:** 2026-06-01
**Total de Atletas:** 0

## 📋 Atletas

| Nombre | Deporte | Estado | Último Sync |
|--------|---------|--------|------------|


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
        