#!/usr/bin/env bash
set -euo pipefail

SKIP_DB=false
for arg in "$@"; do
    [[ "$arg" == "--skip-db" ]] && SKIP_DB=true
done

# Load .env if present
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Create migrations directory
if [ ! -d migrations ]; then
    mkdir -p migrations
    touch migrations/.gitkeep
    echo "✓ Created migrations/ directory"
else
    echo "• migrations/ directory already exists"
fi

# Create yoyo.ini
if [ ! -f yoyo.ini ]; then
    cat > yoyo.ini << 'EOF'
[DEFAULT]
sources = migrations
batch_mode = on
verbosity = 3
EOF
    echo "✓ Created yoyo.ini"
else
    echo "• yoyo.ini already exists"
fi

# Create database if it doesn't exist
if [ "$SKIP_DB" = false ]; then
    PYTHON_CMD="python"
    if command -v uv &> /dev/null; then
        PYTHON_CMD="uv run python"
    fi
    $PYTHON_CMD -c "
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os, sys

db_name = os.environ['DB_NAME']
user = os.environ['DB_USER']
password = os.environ['DB_PASS']
port = os.environ['DB_PORT']
host = os.environ['DB_HOST']

try:
    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname='postgres')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
    if cur.fetchone():
        print(f'• Database \'{db_name}\' already exists')
    else:
        cur.execute(f'CREATE DATABASE \"{db_name}\"')
        print(f'✓ Created database \'{db_name}\'')
    cur.close()
    conn.close()
except Exception as e:
    print(f'⚠  Could not connect to database: {e}', file=sys.stderr)
    print('⚠  Skipping database creation. Make sure your DB server is running.', file=sys.stderr)
"
else
    echo "• Skipping database creation (--skip-db)"
fi

