import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv('MONGODB_URI')
if not uri:
    print('MONGODB_URI not set in .env')
    raise SystemExit(2)

print('MONGODB_URI found (hidden). Attempting connection...')
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    info = client.server_info()
    print('OK: connected to MongoDB server version', info.get('version'))
    dbs = client.list_database_names()
    print('Databases (sample):', dbs[:10])
    raise SystemExit(0)
except Exception as e:
    print('ERROR connecting to MongoDB:', str(e))
    raise SystemExit(1)
