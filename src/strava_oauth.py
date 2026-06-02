import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta
from .config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REDIRECT_URI
from .mongodb_models import db, AthleteManager

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
    def refresh_access_token(strava_id):
        """Refrescar token expirado para el atleta Strava"""
        from cryptography.fernet import Fernet
        import os
        
        athlete = athlete_manager.get_athlete_by_strava_id(strava_id)
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
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            if access_token and refresh_token:
                athlete_manager.update_athlete_tokens(athlete['_id'], access_token, refresh_token)
                return access_token
        return None


class StravaAPIClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.last_status = None

    def _request(self, method, endpoint, params=None):
        response = requests.request(method, f"{STRAVA_API_URL}{endpoint}", headers=self.headers, params=params)
        self.last_status = response.status_code
        return response
    
    def get_athlete_profile(self):
        """Obtener perfil del atleta autenticado"""
        response = self._request("GET", "/athlete")
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
        
        response = self._request("GET", "/athlete/activities", params=params)
        return response.json() if response.status_code == 200 else []
    
    def get_activity_details(self, activity_id):
        """Obtener detalles completos de una actividad"""
        response = self._request("GET", f"/activities/{activity_id}")
        return response.json() if response.status_code == 200 else None
