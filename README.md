# Sistema de Coaching Obsidian + MongoDB + Strava + Telegram

Agente principal para implementar este plan: **@project-builder**

## 🚀 Estructura Implementada

✅ Carpetas creadas:
- `src/` - Scripts principales de Python
- `config/` - Archivos de configuración
- `scripts/` - Utilidades y helpers
- `tests/` - Suite de testing
- `obsidian_templates/` - Plantillas para Obsidian
- `docs/` - Documentación del proyecto
- `.github/agents/` - Agentes personalizados

✅ Modo de uso principal:
- Este sistema se ejecuta como una herramienta de coach.
- El bot de Telegram está pensado para el coach/admin, no para notificar a cada alumno.

✅ Archivos principales creados:
- `src/config.py` - Configuración centralizada
- `src/mongodb_models.py` - Modelos y conexión MongoDB
- `src/strava_oauth.py` - Autenticación OAuth con Strava
- `src/metrics.py` - Cálculos de entrenamientos (TSS, CTL, ATL, TSB)
- `src/strava_sync.py` - Sincronización diaria de actividades
- `src/telegram_bot.py` - Bot de Telegram con Claude AI
- `src/obsidian_writer.py` - Generador de archivos Markdown para Obsidian
- `src/main.py` - Orquestador principal y scheduler
- `requirements.txt` - Dependencias del proyecto
- `.env.template` - Variables de entorno necesarias
- `Dockerfile` - Configuración para deploy en Railway

## 📋 Próximos Pasos

### 1️⃣ Configurar Variables de Entorno
```bash
cp .env.template .env
# Editar .env con tus valores reales
```

### 2️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3️⃣ Generar Clave de Encriptación
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copiar el valor en ENCRYPTION_KEY en .env
```

### 4️⃣ Configurar MongoDB Atlas
- Crear cuenta en https://cloud.mongodb.com
- Crear cluster FREE
- Obtener connection string
- Guardar en MONGODB_URI en .env

### 5️⃣ Crear App Strava
- Ir a https://www.strava.com/settings/api
- Crear nueva aplicación
- Copiar Client ID y Secret a .env

### 6️⃣ Crear Bot Telegram
- Chat con @BotFather en Telegram
- Comando `/newbot`
- Copiar token a TELEGRAM_BOT_TOKEN en .env

### 7️⃣ Obtener API Key Claude
- Ir a https://console.anthropic.com
- Crear nueva API key
- Copiar a CLAUDE_API_KEY en .env

### 8️⃣ Testear Localmente
```bash
python src/main.py
```

## 🏗️ Estructura Final

```
alumnos_BD/
├── .github/
│   └── agents/
│       └── project-builder.agent.md  # Este agente
├── src/
│   ├── config.py
│   ├── mongodb_models.py
│   ├── strava_oauth.py
│   ├── strava_sync.py
│   ├── metrics.py
│   ├── telegram_bot.py
│   ├── obsidian_writer.py
│   └── main.py
├── scripts/
├── tests/
├── obsidian_templates/
├── docs/
├── requirements.txt
├── Dockerfile
├── .env.template
├── .env (crear después de .env.template)
└── PLAN_IMPLEMENTACION_SISTEMA_COACHING.md
```

## 🚀 Deploy en Railway

1. Push a GitHub
2. Conectar repo a Railway
3. Agregar variables de entorno en Railway
4. Railway auto-detecta Dockerfile y deploy

## 📞 Soporte

- MongoDB issues → Ver TROUBLESHOOTING en PLAN_IMPLEMENTACION
- Strava OAuth → Revisar scope `activity:read_all`
- Telegram → Validar token con @BotFather
- Claude API → Verificar créditos en console.anthropic.com

---

**Creado por:** @project-builder  
**Fecha:** 28 Mayo 2026  
**Estado:** ✅ Listo para configurar y ejecutar
