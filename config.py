import os

user = os.environ.get('DB_USER', 'user')
password = os.environ.get('DB_PASSWORD', 'password')
database = os.environ.get('DB_NAME', 'database')
host = os.environ.get('DB_HOST', '127.0.0.1')
port = int(os.environ.get('DB_PORT', 5432))
