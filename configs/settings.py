import os

if os.getenv('WITHIN_DOCKER'):
    MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT', 27017))
    MONGO_DB_HOST = 'mongo_db'
else:
    MONGO_DB_PORT = 27017
    MONGO_DB_HOST = 'localhost'
