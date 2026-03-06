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

### Step 2: Read the system files

4. `CLAUDE.md` — Repo-level ground rules
5. `.mlos/ingest.py` — The vault pipeline (scan, add, write, view, check, export)
6. `.mlos/index.json` — Current index state

### Step 3: Orient

After reading, briefly confirm:
- What you understand the current state to be
- What you think the immediate priorities are
- Any questions before proceeding

### Step 4: Work

Then ask the operator what they want to focus on. Don't assume.

## Key context

- **Two repos**: ClaudeTest (prototypes), Home_Lab_2026 (vault system)
- **Storage**: git-based, repo at https://github.com/mrmeman555/Claude-Cowork-Vault.git
- **Operator**: Mimir (final authority on all changes)
- **Ground rules**: Read first, understand second, suggest third, act only when operator says go
