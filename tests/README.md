# Tests - Suite de Testing

Unittest, pytest y testing de integración para validar:
- Conexión a MongoDB
- OAuth Strava
- Cálculos de métricas
- Sincronización de actividades
- Generación de Obsidian notes
- API de Telegram

## Estructura:
```
tests/
├── test_mongodb.py
├── test_strava.py
├── test_metrics.py
├── test_sync.py
├── test_obsidian.py
└── fixtures/  # Datos de test
```

Run: `pytest -v`
