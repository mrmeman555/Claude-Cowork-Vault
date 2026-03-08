#!/bin/bash
# task.sh — Write-through wrapper for vault task operations.
# Enforces: pull before every read, pull+commit+push after every write.
# Agents should NEVER call ingest.py task commands directly.
#
# Usage:
#   bash .mlos/task.sh list [--project mlos-dev] [--status open] [--tag sync]
#   bash .mlos/task.sh add --project mlos-dev --title "..." [--priority high] [--type task] [--tags a,b] [--notes "..."]
#   bash .mlos/task.sh update <id> [--status done] [--priority high] [--title "..."] [--notes "..."]
#   bash .mlos/task.sh done <id> [--project mlos-dev]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Detect python
PY=""
for cmd in python3 python; do
    if "$cmd" -c "import sys" 2>/dev/null; then
        PY="$cmd"
        break
    fi
done
if [ -z "$PY" ]; then
    echo "Error: Python not found."
    exit 1
fi

INGEST="$PY $REPO_ROOT/.mlos/ingest.py"

# ── Helpers ──────────────────────────────────────────────────

pull() {
    git -C "$REPO_ROOT" pull --rebase origin main --quiet 2>/dev/null || \
    git -C "$REPO_ROOT" pull origin main --quiet 2>/dev/null || \
    echo "[task.sh] Warning: pull failed — proceeding with local state"
}

commit_and_push() {
    local msg="$1"
    cd "$REPO_ROOT"
    git add vault/mlos-dev/tasks.json .mlos/events.jsonl 2>/dev/null
    # Only commit if there are staged changes
    if ! git diff --cached --quiet 2>/dev/null; then
        git commit -m "$msg" --quiet
        # Push, retry once on failure
        if ! git push origin main --quiet 2>/dev/null; then
            echo "[task.sh] Push failed — pulling and retrying..."
            pull
            if ! git push origin main --quiet 2>/dev/null; then
                echo "[task.sh] ERROR: push failed after retry. Changes committed locally but NOT on remote."
                exit 1
            fi
        fi
        echo "[task.sh] Committed and pushed."
    else
        echo "[task.sh] No changes to commit."
    fi
}

# ── Main ─────────────────────────────────────────────────────

if [ $# -lt 1 ]; then
    echo "Usage: bash .mlos/task.sh <list|add|update|done> [args...]"
    echo ""
    echo "Commands:"
    echo "  list   [--project X] [--status X] [--tag X]"
    echo "  add    --project X --title '...' [--priority X] [--type X] [--tags a,b] [--notes '...']"
    echo "  update <id> [--status X] [--priority X] [--title '...'] [--notes '...']"
    echo "  done   <id> [--project X]"
    exit 1
fi

SUBCMD="$1"
shift

case "$SUBCMD" in
    list)
        # Read-only: pull then query
        pull
        $INGEST task list "$@"
        ;;
    add)
        # Write: pull, add, commit+push
        pull
        $INGEST task add "$@"
        # Extract title for commit message
        TITLE=""
        ARGS=("$@")
        for ((i=0; i<${#ARGS[@]}; i++)); do
            if [[ "${ARGS[$i]}" == "--title" ]] && (( i+1 < ${#ARGS[@]} )); then
                TITLE="${ARGS[$((i+1))]}"
                break
            fi
        done
        commit_and_push "task: add — ${TITLE:-new task}"
        ;;
    update)
        # Write: pull, update, commit+push
        pull
        TASK_ID="${1:-}"
        $INGEST task update "$@"
        commit_and_push "task: update ${TASK_ID:-task}"
        ;;
    done)
        # Write: pull, mark done, commit+push
        pull
        TASK_ID="${1:-}"
        $INGEST task done "$@"
        commit_and_push "task: done ${TASK_ID:-task}"
        ;;
    *)
        echo "Unknown command: $SUBCMD"
        echo "Available: list, add, update, done"
        exit 1
        ;;
esac
