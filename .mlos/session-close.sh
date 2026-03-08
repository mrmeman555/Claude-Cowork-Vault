#!/bin/bash
# session-close.sh — ML OS Interactive Session Close
# Location: Home_Lab_2026/.mlos/session-close.sh
# Run this when you're done with a session to commit, merge, and clean up.

set -e

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OPENCLAW_DIR="C:/Users/Erinh/Desktop/OpenClaw_Claude"

# Detect python command
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
echo -e "${AMBER}${BOLD}║         ML OS — SESSION CLOSE             ║${RESET}"
echo -e "${AMBER}${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""

# ─── STEP 1: DETECT CURRENT BRANCH ──────────────────────────────────────────
cd "$OPENCLAW_DIR"
BRANCH=$(git branch --show-current 2>/dev/null)

if [ -z "$BRANCH" ]; then
  echo -e "${RED}Error: Not on any branch (detached HEAD?). Exiting.${RESET}"
  exit 1
fi

if [[ "$BRANCH" != session/* ]]; then
  echo -e "${RED}Error: Not on a session branch.${RESET}"
  echo -e "  Current branch: ${BOLD}$BRANCH${RESET}"
  echo -e "  Session branches start with ${BOLD}session/${RESET}"
  exit 1
fi

# Extract project name from branch (session/{project}/{date}/{id})
PROJECT=$(echo "$BRANCH" | cut -d/ -f2)
SESSION_DATE=$(echo "$BRANCH" | cut -d/ -f3)

echo -e "${GREEN}✓ Session branch: ${BOLD}$BRANCH${RESET}"
echo -e "  ${DIM}Project:${RESET} ${BOLD}$PROJECT${RESET}"
echo -e "  ${DIM}Date:${RESET}    $SESSION_DATE"
echo ""

# ─── STEP 2: DIFF AGAINST MAIN ──────────────────────────────────────────────
echo -e "${AMBER}${BOLD}── SESSION SUMMARY ─────────────────────────${RESET}"
echo ""

# New files (untracked)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null)
if [ -n "$UNTRACKED" ]; then
  echo -e "${CYAN}New files (untracked):${RESET}"
  echo "$UNTRACKED" | while read f; do
    echo -e "  ${GREEN}+${RESET} $f"
  done
  echo ""
fi

# Modified files (vs main)
MODIFIED=$(git diff --name-only main 2>/dev/null)
if [ -n "$MODIFIED" ]; then
  echo -e "${CYAN}Modified files (vs main):${RESET}"
  echo "$MODIFIED" | while read f; do
    echo -e "  ${AMBER}~${RESET} $f"
  done
  echo ""
fi

# Staged files
STAGED=$(git diff --cached --name-only 2>/dev/null)
if [ -n "$STAGED" ]; then
  echo -e "${CYAN}Staged files:${RESET}"
  echo "$STAGED" | while read f; do
    echo -e "  ${GREEN}▸${RESET} $f"
  done
  echo ""
fi

# Check for task changes (if tasks.json exists on this branch vs main)
VAULT_DIR="C:/Users/Erinh/Desktop/Home_Lab_2026/vault"
TASKS_FILE="$VAULT_DIR/$PROJECT/tasks.json"
if [ -f "$TASKS_FILE" ]; then
  # Compare task counts between branch and main
  MAIN_TASKS=$(git show main:"vault/$PROJECT/tasks.json" 2>/dev/null | $PY -c "import sys,json; print(len(json.load(sys.stdin).get('tasks',[])))" 2>/dev/null || echo "0")
  BRANCH_TASKS=$($PY -c "import json; print(len(json.load(open('$TASKS_FILE')).get('tasks',[])))" 2>/dev/null || echo "0")
  if [ "$MAIN_TASKS" != "$BRANCH_TASKS" ]; then
    echo -e "${CYAN}Task changes:${RESET}"
    echo -e "  main: ${MAIN_TASKS} tasks → branch: ${BRANCH_TASKS} tasks"
    echo ""
  fi
fi

# Check if there's anything to commit
if [ -z "$UNTRACKED" ] && [ -z "$MODIFIED" ] && [ -z "$STAGED" ]; then
  echo -e "${DIM}No changes detected on this branch.${RESET}"
  echo ""
fi

# Show commit count on branch
COMMIT_COUNT=$(git rev-list main..HEAD --count 2>/dev/null || echo "0")
echo -e "${DIM}Commits on branch: ${COMMIT_COUNT}${RESET}"
echo ""

# ─── STEP 3: ASK TO MERGE ───────────────────────────────────────────────────
echo -e "${AMBER}${BOLD}────────────────────────────────────────────${RESET}"
read -p "$(echo -e "${BOLD}Merge to main? [y/n]:${RESET} ")" merge_choice

if [[ "$merge_choice" != "y" && "$merge_choice" != "Y" ]]; then
  echo ""
  echo -e "${DIM}Session left open on branch: ${BOLD}$BRANCH${RESET}"
  echo -e "${DIM}Run this script again when ready to close.${RESET}"
  echo ""
  exit 0
fi

# ─── STEP 4: COMMIT, MERGE, CLEAN UP ────────────────────────────────────────
echo ""

# Stage any remaining changes
if [ -n "$UNTRACKED" ] || [ -n "$(git diff --name-only 2>/dev/null)" ]; then
  echo -e "${CYAN}Staging all changes...${RESET}"
  git add -A

  # Ask for commit message
  read -p "$(echo -e "${BOLD}Commit message:${RESET} session: $PROJECT $SESSION_DATE — ")" commit_msg
  if [ -z "$commit_msg" ]; then
    commit_msg="session work"
  fi

  git commit -m "session: $PROJECT $SESSION_DATE — $commit_msg"
  echo -e "${GREEN}✓ Changes committed${RESET}"
fi

# Merge to main
echo -e "${CYAN}Merging to main...${RESET}"
git checkout main --quiet
git merge "$BRANCH" --no-edit --quiet
echo -e "${GREEN}✓ Merged to main${RESET}"

# Push
echo -e "${CYAN}Pushing to remote...${RESET}"
git push origin main --quiet 2>/dev/null
echo -e "${GREEN}✓ Pushed to remote${RESET}"

# Clean up branch
git branch -d "$BRANCH" --quiet 2>/dev/null
echo -e "${GREEN}✓ Branch deleted: $BRANCH${RESET}"

echo ""
echo -e "${AMBER}${BOLD}── SESSION CLOSED ──────────────────────────${RESET}"
echo -e "  ${DIM}Project:${RESET}  ${BOLD}$PROJECT${RESET}"
echo -e "  ${DIM}Branch:${RESET}   ${BOLD}$BRANCH${RESET} → merged to main"
echo -e "  ${DIM}Date:${RESET}     $(date +%Y-%m-%d)"
echo ""
