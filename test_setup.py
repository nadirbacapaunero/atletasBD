#!/usr/bin/env python3
"""
Script para verificar que toda la Semana 1 está configurada correctamente.
Prueba: MongoDB, Strava, Telegram, Claude y Obsidian.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("\n" + "="*60)
print("🔍 VERIFICACIÓN SEMANA 1 - Setup de Servicios Externos")
print("="*60 + "\n")

# 1. VERIFICAR MONGODB
print("1️⃣  MONGODB Atlas")
print("-" * 40)
try:
    from src.mongodb_models import MongoDBConnection
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ MONGODB_URI no configurada")
    else:
        connection = MongoDBConnection()
        # Intentar conexión (acceder a db trigger _ensure_connection)
        db = connection.db
        server_info = connection.client.server_info()
        print("✅ Conexión exitosa a MongoDB")
        print(f"   Version: {server_info.get('version', 'N/A')}")
        # Verificar colecciones creadas
        collections = db.list_collection_names()
        print(f"   Colecciones: {', '.join(collections)}")
except Exception as e:
    print(f"❌ Error con MongoDB: {str(e)}")
    import traceback
    traceback.print_exc()

# 2. VERIFICAR STRAVA
print("\n2️⃣  STRAVA OAuth")
print("-" * 40)
try:
    strava_id = os.getenv("STRAVA_CLIENT_ID")
    strava_secret = os.getenv("STRAVA_CLIENT_SECRET")
    strava_redirect = os.getenv("STRAVA_REDIRECT_URI")

    if not strava_id or not strava_secret:
        print("❌ Credenciales Strava incompletas")
    else:
        print("✅ STRAVA_CLIENT_ID configurado")
        print("✅ STRAVA_CLIENT_SECRET configurado")
        print(f"✅ REDIRECT_URI: {strava_redirect}")
except Exception as e:
    print(f"❌ Error con Strava: {str(e)}")

# 3. VERIFICAR TELEGRAM
print("\n3️⃣  TELEGRAM Bot")
print("-" * 40)
try:
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_admin = os.getenv("TELEGRAM_ADMIN_ID")

    if not telegram_token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
    else:
        print("✅ TELEGRAM_BOT_TOKEN configurado")
        print(f"✅ TELEGRAM_ADMIN_ID: {telegram_admin}")
        # Test rápido del token
        import requests
        response = requests.get(f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=5)
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot conectado: @{bot_info['result']['username']}")
        else:
            print(f"⚠️  Token inválido o sin conexión")
except Exception as e:
    print(f"❌ Error con Telegram: {str(e)}")

# 4. VERIFICAR CLAUDE
print("\n4️⃣  CLAUDE API")
print("-" * 40)
try:
    claude_key = os.getenv("CLAUDE_API_KEY")
    if not claude_key:
        print("❌ CLAUDE_API_KEY no configurada")
    else:
        from anthropic import Anthropic
        client = Anthropic(api_key=claude_key)
        print("✅ CLAUDE_API_KEY configurada")
        print("✅ Cliente Anthropic inicializado")
except Exception as e:
    print(f"❌ Error con Claude: {str(e)}")

# 5. VERIFICAR OBSIDIAN
print("\n5️⃣  OBSIDIAN Vault")
print("-" * 40)
try:
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if not vault_path:
        print("❌ OBSIDIAN_VAULT_PATH no configurada")
    else:
        vault_dir = Path(vault_path)
        if vault_dir.exists():
            print(f"✅ Vault path existe: {vault_path}")
            file_count = len(list(vault_dir.glob("**/*.md")))
            print(f"   Archivos markdown: {file_count}")
        else:
            print(f"⚠️  Vault path no existe: {vault_path}")
except Exception as e:
    print(f"❌ Error con Obsidian: {str(e)}")

# 6. VERIFICAR ENCRYPTION
print("\n6️⃣  ENCRYPTION Key")
print("-" * 40)
try:
    from cryptography.fernet import Fernet
    encryption_key = os.getenv("ENCRYPTION_KEY")
    if not encryption_key:
        print("❌ ENCRYPTION_KEY no configurada")
    else:
        cipher = Fernet(encryption_key.encode())
        test_msg = cipher.encrypt(b"test")
        decrypted = cipher.decrypt(test_msg)
        print("✅ Encryption key válida y funcional")
except Exception as e:
    print(f"❌ Error con Encryption: {str(e)}")

# 7. VERIFICAR SCHEDULER
print("\n7️⃣  SCHEDULER")
print("-" * 40)
try:
    timezone = os.getenv("TIMEZONE")
    sync_time = os.getenv("SYNC_TIME")
    print(f"✅ Timezone: {timezone}")
    print(f"✅ Sync time: {sync_time}")
except Exception as e:
    print(f"❌ Error con Scheduler: {str(e)}")

print("\n" + "="*60)
print("✨ VERIFICACIÓN COMPLETADA")
print("="*60)
print("\n📋 Próximos pasos:")
print("   • Si todo está ✅: Semana 1 COMPLETA")
print("   • Si hay ❌: Configura la variable faltante en .env")
print("   • Luego ejecuta: python src/main.py")
print()
