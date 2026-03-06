# ML OS Development — Pickup Prompt

> Give this to any new Claude session to instantly load project context.
> Works in Claude Code, Cowork, or any Claude interface.

---

## Instructions

You are joining an active development project called **ML OS** (Meta-Language Operating System). Before doing anything, load context.

### Step 1: Read the context pack

Read these files from `vault/mlos-dev/` in order:

1. `project-state.md` — What ML OS is, what exists, where everything lives
2. `decisions.md` — Key architectural decisions and rationale
3. `session-history.md` — What's been done, what's open, what's next
4. `tasks.json` — Current tasks, ideas, and priorities

### Step 2: Read the system files

5. `CLAUDE.md` — Repo-level ground rules
6. `.mlos/ingest.py` — The vault pipeline (scan, add, write, view, check, export, sync, log, task)
7. `.mlos/index.json` — Current index state

### Step 3: Check the vault browser and servers

8. `server.py` — Vault browser API (port 3001)
9. `index.html` — Vault browser frontend (overview, projects, tasks, raw index views)
10. `.claude/launch.json` — Dev server configs (vault-browser on 3001, mlos-demo on 3000)

### Step 4: Orient

After reading, briefly confirm:
- What you understand the current state to be
- What the open tasks are (from tasks.json)
- Any questions before proceeding

### Step 5: Work

Then ask the operator what they want to focus on. Don't assume.

## Key context

- **Two repos**: ClaudeTest (prototypes/ML OS demo), Home_Lab_2026 (vault system)
- **Storage**: git-based, repo at https://github.com/mrmeman555/Claude-Cowork-Vault.git
- **Operator**: Mimir (final authority on all changes)
- **Ground rules**: Read first, understand second, suggest third, act only when operator says go
- **Task tracking**: `python .mlos/ingest.py task list` shows all open tasks
- **Vault browser**: `python server.py` on port 3001, or use `preview_start` with launch.json
- **Context rot warning**: `decisions.md` and `session-history.md` require manual updates — check if they're stale
