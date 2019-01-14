import os

MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT', 27017))
MONGO_DB_HOST = os.getenv('MONGO_DB_HOST', '127.0.0.1')
