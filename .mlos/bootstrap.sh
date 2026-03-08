#!/bin/bash
# bootstrap.sh — ML OS Session Bootstrap
# Location: Home_Lab_2026/.mlos/bootstrap.sh
# Run this at the start of every new chat session in the integrated terminal.

set -e

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT_DIR="$REPO_ROOT/vault"
INGEST="$SCRIPT_DIR/ingest.py"
SERVER="$REPO_ROOT/server.py"
SERVER_PORT=3001
OPENCLAW_DIR="C:/Users/Erinh/Desktop/OpenClaw_Claude"
API_BASE="http://localhost:${SERVER_PORT}/api"

# Detect python command (python3 on Unix, python on Windows)
if command -v python3 &>/dev/null; then
  PY=python3
else
  PY=python
fi

# ─── COLORS ───────────────────────────────────────────────────────────────────
AMBER='\033[0;33m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# ─── HEADER ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${AMBER}${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${AMBER}${BOLD}║         ML OS — SESSION BOOTSTRAP        ║${RESET}"
echo -e "${AMBER}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ─── STEP 1: SELECT PROJECT ───────────────────────────────────────────────────
echo -e "${CYAN}Available projects:${RESET}"
projects=()
i=1
for dir in "$VAULT_DIR"/*/; do
  [ -d "$dir" ] || continue
  project=$(basename "$dir")
  echo -e "  ${AMBER}${i})${RESET} ${project}"
  projects+=("$project")
  ((i++))
done
echo ""

read -p "$(echo -e "${BOLD}Which project is this session for?${RESET} [name or number]: ")" project_input

# resolve number or name
if [[ "$project_input" =~ ^[0-9]+$ ]]; then
  PROJECT="${projects[$((project_input-1))]}"
else
  PROJECT="$project_input"
fi

if [ -z "$PROJECT" ]; then
  echo -e "${RED}No project selected. Exiting.${RESET}"
  exit 1
fi

echo -e "\n${GREEN}✓ Project: ${BOLD}${PROJECT}${RESET}"

# ─── STEP 2: CREATE GIT BRANCH ────────────────────────────────────────────────
DATE=$(date +%Y-%m-%d)
SESSION_ID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 4 | head -n 1)
BRANCH="session/${PROJECT}/${DATE}/${SESSION_ID}"

echo ""
echo -e "${CYAN}Creating session branch on OpenClaw_Claude...${RESET}"

cd "$OPENCLAW_DIR"
git fetch origin main --quiet 2>/dev/null || true
git checkout main --quiet 2>/dev/null
git pull origin main --quiet 2>/dev/null || true
git checkout -b "$BRANCH" --quiet

echo -e "${GREEN}✓ Branch: ${BOLD}${BRANCH}${RESET}"

# ─── STEP 3: START VAULT BROWSER ──────────────────────────────────────────────
echo ""
read -p "$(echo -e "${BOLD}Start vault explorer?${RESET} [y/n]: ")" start_server

if [[ "$start_server" == "y" || "$start_server" == "Y" ]]; then
  # check if already running
  if curl -s "http://localhost:${SERVER_PORT}" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Vault explorer already running${RESET}"
  else
    echo -e "${CYAN}Starting vault explorer...${RESET}"
    cd "$REPO_ROOT"
    $PY server.py &
    sleep 2
    echo -e "${GREEN}✓ Vault explorer started${RESET}"
  fi
  echo -e "  ${AMBER}→ ${CYAN}http://localhost:${SERVER_PORT}${RESET}"
fi

# ─── STEP 4: QUERY PROJECT STATE ──────────────────────────────────────────────
echo ""
echo -e "${CYAN}Loading project state...${RESET}"
echo ""
echo -e "${AMBER}${BOLD}── OPEN TASKS ──────────────────────────────${RESET}"

# Try API first, fall back to direct file read
TASKS_FILE="$VAULT_DIR/$PROJECT/tasks.json"
tasks_json=""

if curl -s "${API_BASE}/tasks" -o /tmp/mlos_tasks.json 2>/dev/null; then
  tasks_json=$(cat /tmp/mlos_tasks.json)
fi

if [ -n "$tasks_json" ] && echo "$tasks_json" | $PY -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
  # Use API response
  $PY -c "
import json, sys
with open('/tmp/mlos_tasks.json') as f:
    tasks = json.load(f)
project_tasks = [t for t in tasks if t.get('project','') == '$PROJECT'
                 and t.get('status','') in ('open','in_progress')]
if not project_tasks:
    print('  No open tasks for this project.')
else:
    for t in sorted(project_tasks, key=lambda x: x.get('priority','') == 'high', reverse=True):
        pri = t.get('priority','').upper()
        status = t.get('status','')
        tid = t.get('id','')[:8]
        title = t.get('title','')
        marker = '\u25b6' if status == 'in_progress' else '\u25cb'
        print(f'  {marker} [{pri}] {title}  {tid}')
"
elif [ -f "$TASKS_FILE" ]; then
  # Fallback: read tasks.json directly
  $PY -c "
import json
with open('$TASKS_FILE') as f:
    data = json.load(f)
tasks = data.get('tasks', [])
open_tasks = [t for t in tasks if t.get('status') in ('open','in_progress')]
if not open_tasks:
    print('  No open tasks for this project.')
else:
    for t in open_tasks:
        marker = '\u25b6' if t.get('status') == 'in_progress' else '\u25cb'
        print(f'  {marker} [{t.get(\"priority\",\"\").upper()}] {t.get(\"title\",\"\")}  {t.get(\"id\",\"\")[:8]}')
"
else
  echo "  No tasks file found for project: $PROJECT"
fi

echo ""
echo -e "${AMBER}${BOLD}── RECENT FILES ────────────────────────────${RESET}"
# list most recently modified files in vault/{project}/
if [ -d "$VAULT_DIR/$PROJECT" ]; then
  ls -t "$VAULT_DIR/$PROJECT"/*.md 2>/dev/null | head -5 | while read f; do
    echo "  ─ $(basename "$f")"
  done
  if ! ls "$VAULT_DIR/$PROJECT"/*.md &>/dev/null; then
    echo "  (no markdown files)"
  fi
else
  echo "  No vault files found for project: $PROJECT"
fi

echo ""
echo -e "${AMBER}${BOLD}── SESSION READY ───────────────────────────${RESET}"
echo -e "  ${DIM}Project:${RESET}  ${BOLD}$PROJECT${RESET}"
echo -e "  ${DIM}Branch:${RESET}   ${BOLD}$BRANCH${RESET}"
echo -e "  ${DIM}Date:${RESET}     $DATE"
echo ""
echo -e "${DIM}When done: commit your work and run${RESET} ${AMBER}session-close.sh${RESET}"
echo ""
