# n8n Integration for Sistema Coaching

Esta carpeta contiene la configuración y los workflows para integrar `Strava`, `Telegram` y `Obsidian` con `n8n`.

## Objetivo

- Sincronizar actividades de Strava diariamente
- Generar notas en Obsidian a partir de los datos sincronizados
- Enviar notificaciones a Telegram cuando el sync finaliza o falla

## Archivos

- `workflows/strava_telegram_obsidian_workflow.json` — workflow n8n de ejemplo para la orquestación diaria

## Pasos para usarlo

1. Importar el workflow `workflows/strava_telegram_obsidian_workflow.json` en n8n.
2. Crear las credenciales necesarias en n8n:
   - `Telegram API` con `TELEGRAM_BOT_TOKEN`
   - `HTTP Request` o `Execute Command` según tu entorno local
3. Asegurar que el repositorio esté disponible para n8n si usas `Execute Command`.
4. Configurar las variables de entorno en el servidor n8n o en los nodos del flujo.
5. Activar el workflow y validar la ejecución manualmente.

## Variables clave

Asegúrate de tener definidas estas variables en `n8n` o en el entorno del nodo:

- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_REDIRECT_URI`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_ADMIN_ID`
- `OBSIDIAN_VAULT_PATH`
- `MONGODB_URI`
- `ENCRYPTION_KEY`
- `TIMEZONE`
- `SYNC_TIME`

## Recomendaciones

- Si utilizas n8n en un servidor distinto al repositorio, adapta la ruta del `Execute Command` o configura un webhook para ejecutar los scripts Python desde una API local.
- Usa la ruta absoluta del vault de Obsidian en `OBSIDIAN_VAULT_PATH`.
- Valida primero el workflow con un gatillo manual antes de activar la ejecución diaria.
