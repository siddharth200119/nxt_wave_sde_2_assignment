# ─── Production Docker Operations ─────────────────────────────────────

# Start production containers in background
prod_up:
    docker compose --env-file .env.prod up -d

# Stop production containers
prod_down:
    docker compose --env-file .env.prod down

# Rebuild and restart production containers
prod_rebuild:
    docker compose --env-file .env.prod up -d --build
