#!/usr/bin/env python3
"""
Watcher Scanner — Find and process new transcripts automatically.

Scans configured transcript sources, identifies unprocessed JSONL files,
and runs the watcher parser on each one.

Usage:
  python .mlos/watcher/scan.py              Scan all sources, parse new transcripts
  python .mlos/watcher/scan.py --dry-run    Show what would be parsed without doing it
  python .mlos/watcher/scan.py --sources    List configured transcript sources
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent.parent  # Home_Lab_2026/
MLOS_DIR = ROOT / ".mlos"
DB_PATH = MLOS_DIR / "watcher.db"
WATCHER_PY = MLOS_DIR / "watcher.py"
EVENTS_LOG = MLOS_DIR / "events.jsonl"

# ── Transcript Sources ────────────────────────────────────────
# Each source is a dict with:
#   path: glob pattern or directory
#   name: human label
#   type: 'glob' (expand pattern) or 'dir' (scan directory for .jsonl)

SOURCES = [
    {
        "name": "Claude Code sessions",
        "path": os.path.expanduser("~/.claude/projects"),
        "type": "recursive",
    },
    {
        "name": "Vault inbox",
        "path": str(ROOT / "io" / "inbox"),
        "type": "dir",
    },
    {
        "name": "OpenClaw inbox",
        "path": str(Path(os.environ.get(
            "OPENCLAW_PATH",
            os.path.expanduser("~/Desktop/OpenClaw_Claude")
        )) / "Inbox"),
        "type": "dir",
    },
]


def is_transcript(path: Path) -> bool:
    """Check if a file looks like a Claude session transcript."""
    if path.suffix != ".jsonl":
        return False
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                return "sessionId" in obj or (
                    obj.get("type") in ("queue-operation", "user", "assistant")
                )
    except (json.JSONDecodeError, IOError, OSError):
        return False
    return False


def get_session_id(path: Path) -> str | None:
    """Extract the session ID from the first relevant line."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                sid = obj.get("sessionId")
                if sid:
                    return sid
    except (json.JSONDecodeError, IOError):
        pass
    return None


def is_already_parsed(session_id: str) -> bool:
    """Check if this session ID is already in the watcher DB."""
    if not DB_PATH.exists():
        return False
    try:
        conn = sqlite3.connect(str(DB_PATH))
        result = conn.execute(
            "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        conn.close()
        return result is not None
    except sqlite3.OperationalError:
        return False


def scan_sources() -> list[dict]:
    """Scan all configured sources and return list of transcript candidates."""
    candidates = []

    for source in SOURCES:
        src_path = Path(source["path"])
        if not src_path.exists():
            continue

        jsonl_files = []
        if source["type"] == "dir":
            jsonl_files = list(src_path.glob("*.jsonl"))
        elif source["type"] == "recursive":
            jsonl_files = list(src_path.rglob("*.jsonl"))

        for f in jsonl_files:
            if f.stat().st_size < 100:  # Skip tiny/empty files
                continue
            if not is_transcript(f):
                continue
            sid = get_session_id(f)
            if not sid:
                continue

            candidates.append({
                "path": str(f),
                "session_id": sid,
                "source": source["name"],
                "size": f.stat().st_size,
                "already_parsed": is_already_parsed(sid),
            })

    return candidates


def parse_transcript(path: str) -> bool:
    """Run watcher.py parse on a transcript file."""
    result = subprocess.run(
        [sys.executable, str(WATCHER_PY), "parse", path],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}", file=sys.stderr)
        return False
    return True


def log_event(new_count: int, total_sessions: int, total_messages: int):
    """Append a watcher_run event to events.jsonl."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "watcher_run",
        "new_sessions": new_count,
        "total_sessions": total_sessions,
        "total_messages": total_messages,
    }
    with open(EVENTS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def get_db_stats() -> dict:
    """Get current DB counts."""
    if not DB_PATH.exists():
        return {"sessions": 0, "messages": 0, "tool_uses": 0}
    conn = sqlite3.connect(str(DB_PATH))
    stats = {}
    for table in ["sessions", "messages", "tool_uses", "files", "decisions", "git_ops", "activities"]:
        try:
            stats[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except sqlite3.OperationalError:
            stats[table] = 0
    conn.close()
    return stats


# ── Main ──────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    show_sources = "--sources" in sys.argv

    if show_sources:
        print("\nConfigured transcript sources:\n")
        for s in SOURCES:
            exists = Path(s["path"]).exists()
            status = "OK" if exists else "NOT FOUND"
            print(f"  [{status}] {s['name']}")
            print(f"         {s['path']}")
            print(f"         Scan: {s['type']}")
            print()
        return

    # Step 1: Current state
    stats = get_db_stats()
    print(f"\n  Current DB: {stats.get('sessions', 0)} sessions, {stats.get('messages', 0)} messages, {stats.get('tool_uses', 0)} tool uses\n")

    # Step 2: Scan
    print("  Scanning transcript sources...")
    candidates = scan_sources()

    new = [c for c in candidates if not c["already_parsed"]]
    existing = [c for c in candidates if c["already_parsed"]]

    print(f"  Found {len(candidates)} transcripts total ({len(new)} new, {len(existing)} already parsed)\n")

    if not new:
        print("  Nothing new to process.")
        return

    for c in new:
        size_kb = c["size"] / 1024
        print(f"  NEW: {c['session_id'][:12]}... ({size_kb:.0f} KB) from {c['source']}")
        print(f"       {c['path']}")

    if dry_run:
        print("\n  [DRY RUN] Would parse the above. Run without --dry-run to execute.")
        return

    # Step 3: Parse
    print(f"\n  Parsing {len(new)} new transcript(s)...\n")
    parsed = 0
    for c in new:
        print(f"  --- {c['session_id'][:12]}... ---")
        if parse_transcript(c["path"]):
            parsed += 1

    # Step 4: Verify
    final_stats = get_db_stats()
    print(f"\n  Final DB: {final_stats.get('sessions', 0)} sessions, {final_stats.get('messages', 0)} messages, {final_stats.get('tool_uses', 0)} tool uses")
    print(f"  Parsed {parsed}/{len(new)} new transcripts.\n")

    # Step 5: Log
    log_event(parsed, final_stats.get("sessions", 0), final_stats.get("messages", 0))
    print("  Logged watcher_run event to events.jsonl.")


if __name__ == "__main__":
    main()
