from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from .strava_oauth import StravaOAuthHandler
from .mongodb_models import db, AthleteManager
from .config import STRAVA_REDIRECT_URI
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

athlete_manager = AthleteManager(db)


@app.get("/callback", response_class=HTMLResponse)
async def strava_callback(request: Request):
    """Endpoint para manejar callback OAuth de Strava.
    Query params: code, state (telegram_user_id)
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    # Intercambiar código por tokens
    token_data = StravaOAuthHandler.exchange_code_for_token(code, state)
    if not token_data:
        raise HTTPException(status_code=500, detail="Failed to exchange code for token")

    strava_id = token_data.get("athlete_strava_id")
    name = token_data.get("athlete_name") or f"strava_{strava_id}"
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if not strava_id or not access_token or not refresh_token:
        raise HTTPException(status_code=500, detail="Incomplete token response from Strava")

    # Buscar atleta existente por strava_id
    athlete = athlete_manager.get_athlete_by_strava_id(strava_id)

    # Si no existe, crear con email único placeholder
    if not athlete:
        placeholder_email = f"strava_{strava_id}@strava.invalid"
        inserted_id = athlete_manager.create_athlete(strava_id, name, placeholder_email)
        if inserted_id:
            athlete_id = inserted_id
        else:
            # Creación falló por duplicado u otro; intentar reconsultar
            athlete = athlete_manager.get_athlete_by_strava_id(strava_id)
            if not athlete:
                raise HTTPException(status_code=500, detail="Failed to create or find athlete")
            athlete_id = athlete.get("_id")
    else:
        athlete_id = athlete.get("_id")

    # Guardar tokens en DB (encryptado por AthleteManager)
    athlete_manager.update_athlete_tokens(athlete_id, access_token, refresh_token)

    # Vincular sesión Telegram si existe (state contiene telegram_user_id)
    try:
        telegram_user_id = int(state)
    except Exception:
        telegram_user_id = None

    if telegram_user_id:
        db.sessions_collection.update_one(
            {"telegram_user_id": telegram_user_id},
            {"$set": {"athlete_id": athlete_id, "state": "authorized"}},
            upsert=False
        )

    html = f"""
    <html>
      <head><title>Autorización Strava completada</title></head>
      <body>
        <h2>✅ Autorización completa</h2>
        <p>Cuenta Strava vinculada: <strong>{name}</strong></p>
        <p>Vuelve a Telegram y usa <strong>/status</strong> o espera al sync nocturno.</p>
      </body>
    </html>
    """

    return HTMLResponse(content=html)
 