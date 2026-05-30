#!/usr/bin/env bash
set -eo pipefail

echo "Checking database connection readiness..."
python -c "
import psycopg2, os, sys, time

db_name = 'postgres'
user = os.environ['DB_USER']
password = os.environ['DB_PASS']
port = os.environ['DB_PORT']
host = os.environ['DB_HOST']

for i in range(30):
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        conn.close()
        print('Database connection established successfully!')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting for database to accept connections... (Attempt {i+1}/30: {e})')
        time.sleep(1)

print('Database not ready after 30 seconds. Exiting.')
sys.exit(1)
"

echo "Initializing database if it does not exist..."
bash scripts/db-init.sh

echo "Applying pending migrations..."
DATABASE_URL="postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"
yoyo apply --batch -d "$DATABASE_URL"

echo "All database migrations applied successfully! Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port 3030
