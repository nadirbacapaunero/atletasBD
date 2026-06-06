# Test Athlete

**ID Strava:** 999999999
**Deporte:** triathlon
**Estado Sync:** pending
**Último Sync:** None

## Datos Personales

| Campo | Valor |
|-------|-------|
| FTP (W) | None |
| LTHR (bpm) | None |
| Peso (kg) | None |
| FC Máx | None |

## Actividades Recientes

```dataview
list
from "Actividades"
where athlete = "Test_Athlete"
sort date descending
limit 10
```

## Métricas

```dataview
table cTL, aTL, tSB
from "Métricas"
where athlete = "Test_Athlete"
sort date descending
limit 5
```

## Reportes

```dataview
list
from "Reportes"
where athlete = "Test_Athlete"
sort date descending
```
        