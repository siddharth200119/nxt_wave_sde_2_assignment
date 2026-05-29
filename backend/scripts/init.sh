#!/usr/bin/env bash
set -euo pipefail

# ─── Colors & Helpers ────────────────────────────────────────────────
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
RESET='\033[0m'

info()    { echo -e "${CYAN}ℹ ${RESET} $1"; }
success() { echo -e "${GREEN}✔ ${RESET} $1"; }
warn()    { echo -e "${YELLOW}⚠ ${RESET} $1"; }
error()   { echo -e "${RED}✖ ${RESET} $1"; }

# ─── Banner ──────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║      🐍  Python Project Init  🐍    ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════╝${RESET}"
echo ""

# ─── Check for uv ────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    error "uv is not installed. Install it from https://docs.astral.sh/uv/"
    exit 1
fi

# ─── Prompt: Project Name ────────────────────────────────────────────
read -rp "$(echo -e "${BOLD}Project name: ${RESET}")" PROJECT_NAME

if [[ -z "$PROJECT_NAME" ]]; then
    error "Project name cannot be empty."
    exit 1
fi

# ─── Prompt: Python Version (default 3.14) ────────────────────────────
read -rp "$(echo -e "${BOLD}Python version ${YELLOW}(default: 3.14)${RESET}: ")" PYTHON_VERSION
PYTHON_VERSION="${PYTHON_VERSION:-3.14}"

# ─── Prompt: Description (optional) ──────────────────────────────────
read -rp "$(echo -e "${BOLD}Description ${YELLOW}(optional)${RESET}: ")" DESCRIPTION

# ─── Prompt: Database (interactive selector) ─────────────────────────
DB_OPTIONS=("PostgreSQL" "MySQL" "MSSQL")
DB_LIBS=("psycopg2-binary" "pymysql" "pymssql")
DB_DIALECTS=("postgresql" "mysql" "mssql")
SELECTED=0
TOTAL=${#DB_OPTIONS[@]}

# Draw the menu
draw_menu() {
    # Move cursor up to overwrite previous menu (skip on first draw)
    if [[ "${1:-}" == "redraw" ]]; then
        for ((i = 0; i < TOTAL; i++)); do
            tput cuu1  # move up
            tput el    # clear line
        done
    fi
    for ((i = 0; i < TOTAL; i++)); do
        if [[ $i -eq $SELECTED ]]; then
            echo -e "  ${GREEN}▸ ${BOLD}${DB_OPTIONS[$i]}${RESET}"
        else
            echo -e "    ${DB_OPTIONS[$i]}"
        fi
    done
}

echo ""
echo -e "${BOLD}Select database: ${YELLOW}(↑/↓ to move, Enter to select)${RESET}"
draw_menu "first"

# Read arrow keys
while true; do
    IFS= read -rsn1 key
    if [[ "$key" == $'\x1b' ]]; then
        read -rsn2 rest
        key+="$rest"
    fi

    case "$key" in
        $'\x1b[A') # Up arrow
            ((SELECTED > 0)) && ((SELECTED--)) || true
            ;;
        $'\x1b[B') # Down arrow
            ((SELECTED < TOTAL - 1)) && ((SELECTED++)) || true
            ;;
        '') # Enter
            break
            ;;
    esac
    draw_menu "redraw"
done

DB_LIB="${DB_LIBS[$SELECTED]}"
DB_DISPLAY="${DB_OPTIONS[$SELECTED]}"
DB_DIALECT="${DB_DIALECTS[$SELECTED]}"
success "Selected ${BOLD}${DB_DISPLAY}${RESET}"

# ─── Init ─────────────────────────────────────────────────────────────
echo ""
info "Initializing git repository..."
git init
success "Git repository initialized!"

info "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv

#Secrets
.env
EOF
success ".gitignore created!"

info "Initializing project with ${BOLD}uv init --bare --python=${PYTHON_VERSION}${RESET} ..."
uv init --bare --python="$PYTHON_VERSION"
success "Project initialized!"

# ─── Update pyproject.toml ────────────────────────────────────────────
if [[ ! -f pyproject.toml ]]; then
    error "pyproject.toml not found after init."
    exit 1
fi

# Update project name
sed -i "s/^name = \".*\"/name = \"${PROJECT_NAME}\"/" pyproject.toml
success "Updated project name to ${BOLD}${PROJECT_NAME}${RESET}"

# Update description if provided
if [[ -n "$DESCRIPTION" ]]; then
    sed -i "s/^description = \".*\"/description = \"${DESCRIPTION}\"/" pyproject.toml
    success "Updated description to ${BOLD}${DESCRIPTION}${RESET}"
fi

# ─── Install dependencies ────────────────────────────────────────────
echo ""
info "Installing dependencies..."

info "Adding ${BOLD}${DB_DISPLAY}${RESET} driver (${DB_LIB})..."
uv add "$DB_LIB"
success "Added ${DB_LIB}"

info "Adding core dependencies..."
uv add fastapi python-dotenv sse-starlette uvicorn psutil redis
success "Added fastapi, python-dotenv, sse-starlette, uvicorn, psutil, redis"

info "Adding dev dependencies..."
uv add --dev yoyo-migrations pytest pytest-asyncio
success "Added yoyo-migrations, pytest, pytest-asyncio"

# ─── Append pytest config to pyproject.toml ───────────────────────────
echo "" >> pyproject.toml
cat >> pyproject.toml << 'EOF'
[tool.pytest.ini_options]
pythonpath = [".", "src"]
asyncio_mode = "auto"
EOF
success "Added pytest config to pyproject.toml"

# ─── Prompt: Configure Database? ──────────────────────────────────────
echo ""
read -rp "$(echo -e "${BOLD}Configure database credentials? ${YELLOW}(y/N)${RESET}: ")" CONFIGURE_DB

# Derive a default DB name from the project name (replace hyphens with underscores)
DEFAULT_DB_NAME=$(echo "$PROJECT_NAME" | tr '-' '_')

if [[ "$CONFIGURE_DB" =~ ^[Yy]$ ]]; then
    # ─── Prompt: Database Credentials ─────────────────────────────────
    echo ""
    echo -e "${BOLD}Database credentials:${RESET}"

    read -rp "$(echo -e "  ${BOLD}DB Host ${YELLOW}(default: localhost)${RESET}: ")" INPUT_DB_HOST
    read -rp "$(echo -e "  ${BOLD}DB Port ${YELLOW}(default: 5432)${RESET}: ")" INPUT_DB_PORT
    read -rp "$(echo -e "  ${BOLD}DB User ${YELLOW}(default: postgres)${RESET}: ")" INPUT_DB_USER
    read -rsp "$(echo -e "  ${BOLD}DB Password ${YELLOW}(default: postgres)${RESET}: ")" INPUT_DB_PASS
    echo ""
    read -rp "$(echo -e "  ${BOLD}DB Name ${YELLOW}(default: ${DEFAULT_DB_NAME})${RESET}: ")" INPUT_DB_NAME

    FINAL_DB_HOST="${INPUT_DB_HOST:-localhost}"
    FINAL_DB_PORT="${INPUT_DB_PORT:-5432}"
    FINAL_DB_USER="${INPUT_DB_USER:-postgres}"
    FINAL_DB_PASS="${INPUT_DB_PASS:-postgres}"
    FINAL_DB_NAME="${INPUT_DB_NAME:-$DEFAULT_DB_NAME}"

    # ─── Create .env file ─────────────────────────────────────────────
    echo ""
    info "Creating .env file..."

    cat > .env << EOF
# ─── Database ─────────────────────────────────────────────────
DB_DIALECT=${DB_DIALECT}
DB_NAME=${FINAL_DB_NAME}
DB_USER=${FINAL_DB_USER}
DB_PASS=${FINAL_DB_PASS}
DB_PORT=${FINAL_DB_PORT}
DB_HOST=${FINAL_DB_HOST}

# ─── Redis ────────────────────────────────────────────────────
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ─── Server ──────────────────────────────────────────────────
SERVICE_NAME=${PROJECT_NAME}
PORT=8000
HOST=127.0.0.1
ENV=DEV
EOF
    success "Created .env file"

    # ─── Run db-init script ───────────────────────────────────────────
    echo ""
    info "Running database init script..."
    bash scripts/db-init.sh
    success "Database initialized!"
else
    # ─── Create .env with placeholders ────────────────────────────────
    echo ""
    info "Creating .env file with defaults..."

    cat > .env << EOF
# ─── Database ─────────────────────────────────────────────────
DB_DIALECT=${DB_DIALECT}
DB_NAME=${DEFAULT_DB_NAME}
DB_USER=postgres
DB_PASS=postgres
DB_PORT=5432
DB_HOST=localhost

# ─── Redis ────────────────────────────────────────────────────
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ─── Server ──────────────────────────────────────────────────
SERVICE_NAME=${PROJECT_NAME}
PORT=8000
HOST=127.0.0.1
ENV=DEV
EOF
    success "Created .env file"

    # ─── Run db-init script ───────────────────────────────────────────
    echo ""
    info "Setting up migrations..."
    bash scripts/db-init.sh --skip-db
fi

echo ""
echo -e "${GREEN}${BOLD}🎉 All done! Happy coding.${RESET}"
echo ""
