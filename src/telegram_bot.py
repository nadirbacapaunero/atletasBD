import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_BOT_TOKEN, CLAUDE_API_KEY, OBSIDIAN_VAULT_PATH
from .mongodb_models import db, AthleteManager
from .strava_oauth import StravaOAuthHandler
from .strava_sync import StravaSyncService
from .obsidian_writer import update_obsidian_vault
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
/sync - Forzar sincronización de Strava y actualizar Obsidian
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

Una vez autorizado, sincronizaré automáticamente tus entrenamientos cada noche a las 21:00.
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
    async def sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /sync - Forzar sincronización de Strava"""
        user = update.effective_user
        
        session = db.sessions_collection.find_one({"telegram_user_id": user.id})
        if not session or not session.get('athlete_id'):
            await update.message.reply_text("❌ Primero conecta tu cuenta Strava con /register")
            return
        
        athlete = db.athletes_collection.find_one({"_id": session['athlete_id']})
        if not athlete:
            await update.message.reply_text("❌ No se encontró el atleta en la base de datos.")
            return
        
        await update.message.reply_text("🔄 Iniciando sincronización de Strava...")
        service = StravaSyncService()
        new_count = service.sync_athlete(session['athlete_id'], athlete['strava_id'])
        await update_obsidian_vault(OBSIDIAN_VAULT_PATH)

        await update.message.reply_text(
            f"✅ Sincronización finalizada. {new_count} actividades nuevas importadas."
        )

    @staticmethod
    async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /weekly - Resumen semanal"""
        user = update.effective_user
        
        session = db.sessions_collection.find_one({"telegram_user_id": user.id})
        if not session or not session.get('athlete_id'):
            await update.message.reply_text("❌ Conecta con /register primero")
            return
        
        from .metrics import MetricsCalculator
        
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
    app.add_handler(CommandHandler("sync", CoachingBot.sync))
    app.add_handler(CommandHandler("status", CoachingBot.status))
    app.add_handler(CommandHandler("weekly", CoachingBot.weekly))
    app.add_handler(CommandHandler("ask", CoachingBot.ask))
    
    return app


# Para ejecutar
if __name__ == "__main__":
    app = create_app()
    app.run_polling()
