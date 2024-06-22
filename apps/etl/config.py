import os

SIZE_CHUNK = 100

POSTGRES_DBNAME = os.environ.get('DB_NAME', 'postgres')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'example')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))

ELASTIC_HOST = os.environ.get('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
