# ML OS — How This Thing Actually Works
*Written for Mimir. Read this when you're foggy, sick, or just lost.*

---

## The Big Picture

You have a personal infrastructure system that persists knowledge across AI sessions. The core problem it solves: every new Claude session starts cold with no memory. ML OS fixes that by keeping state in git repos that any agent can pull and read.

There are two repos. A task system. A sync layer. A query layer. That's basically it.

---

## The Two Repos

### Claude-Cowork-Vault (local folder: `Home_Lab_2026`)

This is the **vault** — your persistent storage. It holds:
- `vault/mlos-dev/tasks.json` — all your tasks
- `vault/mlos-dev/decisions.md` — architectural decisions log
- `vault/mlos-dev/project-state.md` — auto-generated project snapshot
- `.mlos/` — all the tooling (task.sh, watcher.py, ingest.py, merge driver, sync scripts)

When an agent does work — creates a task, updates a task, logs an event — it writes here and pushes to GitHub. This is the write path.

**Local paths:**
- Windows: `Z:\Projects\ML_OS\Home_Lab_2026`
- Linux: `/mnt/share/Projects/ML_OS/Home_Lab_2026`

**Remote:** `https://github.com/mrmeman555/Claude-Cowork-Vault.git`

Note: the local folder is called `Home_Lab_2026` but the GitHub repo is `Claude-Cowork-Vault`. They match. Don't let the name mismatch confuse you.

---

### OpenClaw_Claude

This is the **agent brain** — it holds:
- `CLAUDE.md` — the boot sequence every Claude Code agent reads at startup
- `.claude/commands/` — slash commands (`/sync`, `/setup-sync`)
- `.claude/INBOX.md` — notes left by cloud agents for local agents to read
- `Inbox/` — untracked docs, PDFs, design notes (not committed yet)

This repo is what makes Claude Code "smart" when it boots — it reads CLAUDE.md and knows the whole protocol.

**Local paths:**
- Windows: `Z:\Projects\ML_OS\OpenClaw_Claude`
- Linux: `/mnt/share/Projects/ML_OS/OpenClaw_Claude`

**Remote:** `https://github.com/mrmeman555/OpenClaw_Claude.git`

---

## The Task System

### task.sh — the only right way to touch tasks

`task.sh` is a wrapper script in `.mlos/`. Every task operation goes through it. It enforces this sequence automatically:

1. Pull from remote (so you have latest state)
2. Make the change (add/update/complete)
3. Commit `tasks.json` and `events.jsonl`
4. Push to GitHub
5. Retry once if push fails

**You never call `ingest.py` directly for tasks.** That bypasses the pull-before-write safety.

**Usage:**
```bash
# From vault root on either device
bash .mlos/task.sh list --project mlos-dev
bash .mlos/task.sh add --project mlos-dev --title "..." --priority high --type task --notes "..."
bash .mlos/task.sh done <task-id>
```

### The fragility to know about

If you create tasks from the **claude.ai web interface** (like this chat), those go through a different path — Claude's sandbox, not your local machine. That means no `task.sh`, no pull-before-write, no merge driver protection. It works until it causes a conflict. This is a known temporary risk while you're still web-dependent.

---

## The Two-Layer Principle

This is the core architectural idea. Everything follows from it:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Write path | Git + GitHub | Source of truth. Immutable history. Multi-device sync. |
| Read path | SQLite (`watcher.db`) | Fast queries. Derived from git. Rebuildable any time. |

Git is never wrong. SQLite can be stale or corrupted — just rebuild it from git and it's fine again. If the vault browser shows the wrong task count, the problem is SQLite, not git.

---

## How the Two Devices Stay in Sync

Both devices point to the same GitHub remote. Sync happens through git pull/push.

**For tasks:** `task.sh` pulls before every write and pushes after. So as long as you use task.sh, devices stay in sync automatically.

**For transcripts:** Background sync runs continuously:
- Linux: `~/.mlos/transcript-sync.sh` runs every 1 minute via cron, rsyncing Claude transcripts to the shared drive at `/mnt/share/Projects/ML_OS/transcripts/device-2/`
- Windows: Scheduled task `MLOS-TranscriptSync` runs robocopy every 1 minute, copying to `Z:\Projects\ML_OS\transcripts\device-1\`

**For conflict resolution:** The merge driver (`.mlos/merge-driver.py`) handles the two files that conflict most — `tasks.json` (merges by task ID, newer timestamp wins) and `events.jsonl` (concatenates, deduplicates, sorts). It's registered in `.gitattributes`. Each device needs to register it locally — it's not committed to git because it's a local git config thing.

---

## The Vault Browser

A local web server at `server.py` in the vault root. Runs on port 3001. Reads from SQLite. Lets you see tasks, project state, transcripts in a browser at `http://localhost:3001`.

Starts either manually (`python server.py`) or via `bootstrap.sh` when it asks "Start vault explorer?"

If the task count looks wrong — restart the server. It's reading stale SQLite.

---

## How to Start a Session

**Claude Code (local, recommended):**
```bash
cd /mnt/share/Projects/ML_OS/Home_Lab_2026   # Linux
# or
cd Z:\Projects\ML_OS\Home_Lab_2026            # Windows

bash .mlos/bootstrap.sh
```

Then inside Claude Code, run `/sync` to check both repos and surface what's changed.

**Web interface (claude.ai):**
Just open the project. Remember: task creation here bypasses task.sh. Use it for thinking and planning, not task writes — or accept the fragility and fix conflicts if they happen.

---

## What Breaks and Why

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Push rejected / non-fast-forward | Remote has commits your local doesn't | `git pull --rebase` then push again |
| Vault browser shows wrong task count | SQLite is stale | Restart server.py |
| Task created from web chat didn't persist | Web chat used ingest.py directly, not task.sh | Check git log; if it pushed fine, just pull on local devices |
| New session has no context | Opened wrong project in claude.ai, or CLAUDE.md not read | Make sure you're in the right project; Claude Code reads CLAUDE.md on boot |
| Merge conflict on tasks.json | Two devices pushed without pulling first | Merge driver should handle it; if not, manually keep the newer task entries |
| Transcripts not syncing | Cron/scheduled task not running | Linux: check `crontab -l`; Windows: check Task Scheduler for `MLOS-TranscriptSync` |

---

## The Files That Matter Most

```
Claude-Cowork-Vault/
├── vault/mlos-dev/
│   ├── tasks.json          ← all tasks, source of truth
│   ├── decisions.md        ← why things are the way they are
│   └── project-state.md    ← auto-generated snapshot
├── .mlos/
│   ├── task.sh             ← ONLY way to touch tasks
│   ├── watcher.py          ← ingests transcripts → SQLite
│   ├── ingest.py           ← underlying task/event engine (don't call directly)
│   ├── merge-driver.py     ← handles git conflicts on tasks.json + events.jsonl
│   ├── bootstrap.sh        ← session start script
│   └── session-close.sh    ← session end script
├── server.py               ← vault browser backend
├── index.html              ← vault browser frontend
└── .gitattributes          ← tells git to use merge driver

OpenClaw_Claude/
├── CLAUDE.md               ← agent boot sequence
└── .claude/
    ├── INBOX.md            ← cloud-to-local agent messages
    └── commands/
        ├── sync.md         ← /sync command
        └── setup-sync.md   ← /setup-sync command
```

---

## The North Star

The long-term goal is a custom chat interface that replaces claude.ai entirely — with the vault browser, knowledge graph, and terminal all in one window. Until then, the web interface is a temporary dependency with known fragility. Every system decision is made with that future in mind: git as the spine, SQLite as the query layer, agents as interchangeable inference engines.

---

*Last updated: 2026-03-09*
*Task: t-19c06d*
