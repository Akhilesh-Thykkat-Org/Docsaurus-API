#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color
YELLOW='\033[1;33m'

echo -e "${GREEN}Starting Docs Automation API...${NC}"

# 1. Check for .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found! Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env with your credentials.${NC}"
fi

# 2. Dependency Management
if command -v uv &> /dev/null; then
    echo -e "${GREEN}Using 'uv' for dependency management...${NC}"
    uv sync
else
    echo -e "${YELLOW}'uv' not found. Falling back to pip/venv...${NC}"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# 3. Run Server
echo -e "${GREEN}Starting Uvicorn server...${NC}"

# Check if uv is used to run, otherwise standard
if command -v uv &> /dev/null; then
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    source .venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi
