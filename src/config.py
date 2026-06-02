import os
from dotenv import load_dotenv

load_dotenv()

# ==================== MONGODB ====================
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "coaching_db")

# ==================== STRAVA ====================
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:8000/callback")

# ==================== TELEGRAM ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
_tele_admin = os.getenv("TELEGRAM_ADMIN_ID", "0")
try:
	TELEGRAM_ADMIN_ID = int(_tele_admin) if _tele_admin != "" else 0
except ValueError:
	TELEGRAM_ADMIN_ID = 0

# ==================== CLAUDE ====================
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# ==================== OBSIDIAN ====================
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "/path/to/vault")

# ==================== SCHEDULER ====================
SYNC_TIME = "21:00"  # Buenos Aires 21:00 hs
TIMEZONE = "America/Argentina/Buenos_Aires"

# ==================== SECURITY ====================
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
