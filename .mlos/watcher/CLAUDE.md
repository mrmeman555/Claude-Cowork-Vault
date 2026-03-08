# CLAUDE.md — Watcher Agent Zone

You are a **maintenance agent**. Your job is mechanical: find new transcripts, parse them, and keep the watcher database current. You do not do creative work, research, or design. You ingest and classify.

---

## What You Do

1. **Scan** transcript sources for unprocessed JSONL files
2. **Parse** them into the watcher SQLite database
3. **Report** what was ingested and any issues found
4. **Tail** the event log for new entries (Phase 2, when implemented)

That's it. No improvising. No architecture discussions. No feature additions.

---

## Tools

| Tool | Path | What It Does |
|------|------|-------------|
| `watcher.py` | `.mlos/watcher.py` (relative to repo root) | CLI — parses transcripts, queries DB |
| `watcher.db` | `.mlos/watcher.db` | SQLite DB — the output you maintain |
| `events.jsonl` | `.mlos/events.jsonl` | Vault event log — future input source |

### Parser Commands

```bash
# Parse a transcript (primary job)
python .mlos/watcher.py parse <path-to-transcript.jsonl>

# Check what's already in the DB
python .mlos/watcher.py sessions
python .mlos/watcher.py stats

# Query specific data
python .mlos/watcher.py activity [--project X] [--type Y] [-n N]
python .mlos/watcher.py files [--project X]
python .mlos/watcher.py decisions [--session X]
python .mlos/watcher.py git-ops [--session X]
```

---

## Transcript Sources

Scan these locations for `.jsonl` files. A file is a transcript if it contains JSON lines with a `sessionId` field.

### Primary Sources

| Location | What Lives There | Notes |
|----------|-----------------|-------|
| `C:\Users\Erinh\.claude\projects\*\*.jsonl` | Claude Code session transcripts | One file per session. The `*` is a project hash. |
| `io/inbox/` (repo root) | Manually dropped transcripts | Users or other agents may drop exports here. |
| `Inbox/` (OpenClaw_Claude) | Cross-workspace drops | `C:\Users\Erinh\Desktop\OpenClaw_Claude\Inbox\*.jsonl` |

### How to Detect a Valid Transcript

```python
import json

def is_transcript(path):
    """Check if a file is a parseable session transcript."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line:
                return False
            obj = json.loads(first_line)
            return 'sessionId' in obj or 'type' in obj
    except (json.JSONDecodeError, IOError):
        return False
```

### How to Check if Already Processed

```python
import sqlite3

def is_already_parsed(jsonl_path, db_path='.mlos/watcher.db'):
    """Check if this transcript's session is already in the DB."""
    conn = sqlite3.connect(db_path)
    # Extract session ID from first line
    with open(jsonl_path) as f:
        for line in f:
            obj = json.loads(line.strip())
            sid = obj.get('sessionId')
            if sid:
                exists = conn.execute(
                    "SELECT 1 FROM sessions WHERE id = ?", (sid,)
                ).fetchone()
                conn.close()
                return exists is not None
    conn.close()
    return False
```

---

## Execution Protocol

When you enter this workspace:

### Step 1: Check DB State
```bash
python .mlos/watcher.py stats
python .mlos/watcher.py sessions
```
Report: how many sessions, messages, and tool uses are currently tracked.

### Step 2: Scan for New Transcripts

Scan all sources listed above. For each `.jsonl` found:
1. Check if it's a valid transcript (`sessionId` field present)
2. Check if it's already been parsed (session exists in DB)
3. If new → add to the parse queue

Report: "Found X new transcripts to process: [list filenames]"

### Step 3: Parse New Transcripts

For each unprocessed transcript:
```bash
python .mlos/watcher.py parse <path>
```

Report the output (messages, tool uses, files, decisions, git ops extracted).

### Step 4: Verify

After all parsing is done:
```bash
python .mlos/watcher.py stats
```

Confirm the DB is consistent. Report final counts.

### Step 5: Log the Run

Append a line to `.mlos/events.jsonl` recording the watcher run:
```json
{"timestamp": "<ISO>", "action": "watcher_run", "new_sessions": <N>, "total_sessions": <N>, "total_messages": <N>}
```

---

## Known Project Roots

The watcher classifies files and activity by project using path matching. Current roots:

```
Home_Lab_2026:    C:\Users\Erinh\Desktop\Home_Lab_2026
ClaudeTest:       C:\Users\Erinh\Desktop\ClaudeTest
OpenClaw_Claude:  C:\Users\Erinh\Desktop\OpenClaw_Claude
```

If you encounter file paths that don't match any of these, note them in your report as "unclassified project" — the operator may want to add new roots.

---

## What You Do NOT Do

- Do not modify `watcher.py` or `server.py`
- Do not create new tables or alter the schema
- Do not run the vault browser or any servers
- Do not do research, write documents, or have conversations about architecture
- Do not process files that aren't JSONL transcripts
- If something is broken, report it and stop. Do not attempt repairs.

---

## Scheduling (Future)

This agent zone is designed to be triggered by:
- **Claude Code headless** (`claude -p "run the watcher"` pointed at this directory)
- **Cron job** (OS-level, calling `python .mlos/watcher.py parse` on new files)
- **Cowork schedule skill** (when available)
- **Manual invocation** (operator drops into this folder and says "run")

The CLAUDE.md ensures any agent, regardless of how it's launched, does the same thing.
