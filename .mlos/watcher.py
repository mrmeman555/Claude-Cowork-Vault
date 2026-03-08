#!/usr/bin/env python3
"""
ML OS — Programmatic Context Watcher (Phase 1)

Parses Claude Code JSONL transcripts into a SQLite database,
extracting structured signals without any LLM dependency.

Usage:
  python .mlos/watcher.py parse <transcript.jsonl>   Parse a transcript into the DB
  python .mlos/watcher.py sessions                    List all parsed sessions
  python .mlos/watcher.py activity [--project X] [--type Y] [-n N]  Query activity timeline
  python .mlos/watcher.py files [--project X]         List files by project
  python .mlos/watcher.py decisions [--session X]     List extracted decisions
  python .mlos/watcher.py stats [--session X]         Session statistics
  python .mlos/watcher.py git-ops [--session X]       Git operation history
"""

import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
MLOS_DIR = ROOT / ".mlos"
DB_PATH = MLOS_DIR / "watcher.db"

# ── Project Classification ────────────────────────────────────

def _load_env():
    """Load .env from repo root for device-local paths."""
    env_path = ROOT / ".env"
    env_vars = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()
    return env_vars

def _build_project_roots():
    """Build PROJECT_ROOTS from .env, with both slash variants for matching."""
    env = _load_env()
    home_lab = env.get("MLOS_ROOT", os.environ.get("MLOS_ROOT", "")) + "/Home_Lab_2026"
    claudetest = env.get("CLAUDETEST_DIR", os.environ.get("CLAUDETEST_DIR", ""))
    openclaw = env.get("OPENCLAW_DIR", os.environ.get("OPENCLAW_DIR", ""))

    roots = {}
    for name, path in [("Home_Lab_2026", home_lab), ("ClaudeTest", claudetest), ("OpenClaw_Claude", openclaw)]:
        if path:
            fwd = path.replace("\\", "/")
            bck = path.replace("/", "\\")
            roots[name] = [fwd, bck]
    return roots

PROJECT_ROOTS = _build_project_roots()


def classify_project(path: str) -> str | None:
    if not path:
        return None
    normalized = path.replace("\\", "/")
    for project, roots in PROJECT_ROOTS.items():
        for root in roots:
            if normalized.startswith(root.replace("\\", "/")):
                return project
    return None


# ── Activity Classification ───────────────────────────────────

TOOL_ACTIVITY_MAP = {
    "Write": "create",
    "Edit": "modify",
    "Read": "read",
    "Glob": "query",
    "Grep": "query",
    "Bash": "execute",
    "TodoWrite": "plan",
    "AskUserQuestion": "decide",
    "Task": "delegate",
    "TaskOutput": "delegate",
    "EnterPlanMode": "plan",
    "ExitPlanMode": "plan",
    "NotebookEdit": "modify",
}


def classify_bash(command: str) -> str:
    if not command:
        return "execute"
    cmd = command.lower()
    if "git commit" in cmd:
        return "git_commit"
    if "git push" in cmd:
        return "git_push"
    if "git pull" in cmd:
        return "git_pull"
    if "git clone" in cmd:
        return "git_clone"
    if "git" in cmd:
        return "git_other"
    if "pip install" in cmd or "npm install" in cmd:
        return "install"
    if cmd.startswith("python") or cmd.startswith("node"):
        return "run"
    if "ls " in cmd or "cat " in cmd or "head " in cmd or "tail " in cmd:
        return "read"
    if "mkdir " in cmd or "cp " in cmd or "mv " in cmd:
        return "create"
    if "rm " in cmd:
        return "delete"
    return "execute"


# ── Git Operation Parsing ─────────────────────────────────────

GIT_PATTERNS = [
    (r'git commit\s+.*?-m\s+["\'](.+?)["\']', "commit"),
    (r"git commit\s+.*?-m\s+(\S+)", "commit"),
    (r"git push\s+(\S+)\s+(\S+)", "push"),
    (r"git push", "push"),
    (r"git pull\s+(\S+)\s+(\S+)", "pull"),
    (r"git pull", "pull"),
    (r"git checkout\s+(-b\s+)?(\S+)", "checkout"),
    (r"git branch\s+(\S+)", "branch"),
    (r"git merge\s+(\S+)", "merge"),
    (r"git clone\s+(\S+)", "clone"),
    (r"git add\s+(.+)", "add"),
    (r"git status", "status"),
    (r"git diff", "diff"),
    (r"git log", "log"),
    (r"git remote\s+(.+)", "remote"),
    (r"git init", "init"),
]


def parse_git_op(command: str) -> dict | None:
    if "git" not in command.lower():
        return None
    for pattern, op_type in GIT_PATTERNS:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            return {"operation": op_type, "detail": match.group(0)[:200]}
    return None


# ── Decision Extraction ───────────────────────────────────────


def extract_decision(tool_input: dict) -> dict | None:
    questions = tool_input.get("questions", [])
    answers = tool_input.get("answers", {})
    if questions:
        q = questions[0]
        return {
            "question": q.get("question", ""),
            "answer": list(answers.values())[0] if answers else None,
            "options": [o.get("label") for o in q.get("options", [])],
        }
    return None


# ── Database Schema ───────────────────────────────────────────


def init_db(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
        """
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        transcript_path TEXT NOT NULL,
        cwd TEXT,
        git_branch TEXT,
        started_at TEXT,
        ended_at TEXT,
        message_count INTEGER DEFAULT 0,
        tool_use_count INTEGER DEFAULT 0,
        meta JSON
    );

    CREATE TABLE IF NOT EXISTS messages (
        uuid TEXT PRIMARY KEY,
        session_id TEXT REFERENCES sessions(id),
        parent_uuid TEXT,
        type TEXT NOT NULL,
        role TEXT,
        timestamp TEXT NOT NULL,
        cwd TEXT,
        content_preview TEXT,
        has_tool_use INTEGER DEFAULT 0,
        meta JSON
    );

    CREATE TABLE IF NOT EXISTS tool_uses (
        id TEXT PRIMARY KEY,
        message_uuid TEXT REFERENCES messages(uuid),
        session_id TEXT REFERENCES sessions(id),
        tool_name TEXT NOT NULL,
        timestamp TEXT,
        file_path TEXT,
        command TEXT,
        activity_type TEXT,
        project TEXT,
        meta JSON
    );

    CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY,
        project TEXT,
        first_seen TEXT,
        last_seen TEXT,
        read_count INTEGER DEFAULT 0,
        write_count INTEGER DEFAULT 0,
        edit_count INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT REFERENCES sessions(id),
        message_uuid TEXT REFERENCES messages(uuid),
        timestamp TEXT,
        question TEXT,
        answer TEXT,
        project TEXT,
        meta JSON
    );

    CREATE TABLE IF NOT EXISTS git_ops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT REFERENCES sessions(id),
        tool_use_id TEXT REFERENCES tool_uses(id),
        timestamp TEXT,
        operation TEXT,
        detail TEXT,
        project TEXT
    );

    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT REFERENCES sessions(id),
        timestamp TEXT,
        type TEXT,
        target TEXT,
        project TEXT,
        source_type TEXT,
        source_id TEXT,
        meta JSON
    );

    CREATE INDEX IF NOT EXISTS idx_tool_uses_session ON tool_uses(session_id);
    CREATE INDEX IF NOT EXISTS idx_tool_uses_project ON tool_uses(project);
    CREATE INDEX IF NOT EXISTS idx_tool_uses_tool ON tool_uses(tool_name);
    CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
    CREATE INDEX IF NOT EXISTS idx_files_project ON files(project);
    CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project);
    CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(type);
    CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON activities(timestamp);
    """
    )
    conn.commit()
    return conn


# ── JSONL Parser ──────────────────────────────────────────────


def parse_transcript(jsonl_path: str, conn: sqlite3.Connection) -> dict:
    """Parse a Claude Code JSONL transcript into the database.

    Returns stats dict with counts of records created.
    """
    path = Path(jsonl_path)
    if not path.exists():
        raise FileNotFoundError(f"Transcript not found: {jsonl_path}")

    stats = {
        "messages": 0,
        "tool_uses": 0,
        "files": 0,
        "decisions": 0,
        "git_ops": 0,
        "activities": 0,
    }

    # First pass: collect session metadata
    session_id = None
    first_ts = None
    last_ts = None
    primary_cwd = None
    git_branch = None
    message_count = 0
    tool_use_count = 0

    lines = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                lines.append(obj)
            except json.JSONDecodeError:
                continue

    # Extract session metadata from first relevant message
    for obj in lines:
        if obj.get("sessionId"):
            session_id = obj["sessionId"]
        if obj.get("cwd") and not primary_cwd:
            primary_cwd = obj["cwd"]
        if obj.get("gitBranch") and not git_branch:
            git_branch = obj["gitBranch"]
        ts = obj.get("timestamp")
        if ts:
            if not first_ts:
                first_ts = ts
            last_ts = ts
        if session_id and primary_cwd:
            break

    if not session_id:
        session_id = path.stem  # fallback to filename

    # Check if session already exists
    existing = conn.execute(
        "SELECT id FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    if existing:
        print(f"  Session {session_id} already in DB — skipping.")
        return stats

    # Count messages and tool uses
    for obj in lines:
        if obj.get("type") in ("user", "assistant", "system"):
            message_count += 1
        msg = obj.get("message", {})
        if isinstance(msg, dict):
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_use_count += 1

    # Insert session
    conn.execute(
        """INSERT INTO sessions (id, transcript_path, cwd, git_branch,
           started_at, ended_at, message_count, tool_use_count, meta)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            str(path),
            primary_cwd,
            git_branch,
            first_ts,
            last_ts,
            message_count,
            tool_use_count,
            json.dumps({"version": lines[0].get("version") if lines else None}),
        ),
    )

    # Second pass: process each line
    for obj in lines:
        obj_type = obj.get("type")
        ts = obj.get("timestamp")
        uuid = obj.get("uuid")
        cwd = obj.get("cwd")

        # Skip queue-operation and progress types for message table
        if obj_type in ("queue-operation", "progress"):
            continue

        if obj_type not in ("user", "assistant", "system"):
            continue

        # Extract content preview
        msg = obj.get("message", {})
        preview = ""
        has_tool_use = False

        if isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, str):
                preview = content[:200]
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            if not preview:
                                preview = block.get("text", "")[:200]
                        elif block.get("type") == "tool_use":
                            has_tool_use = True
                    elif isinstance(block, str) and not preview:
                        preview = block[:200]

        # Insert message
        if uuid:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO messages
                       (uuid, session_id, parent_uuid, type, role, timestamp,
                        cwd, content_preview, has_tool_use, meta)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        uuid,
                        session_id,
                        obj.get("parentUuid"),
                        obj_type,
                        msg.get("role") if isinstance(msg, dict) else None,
                        ts,
                        cwd,
                        preview,
                        1 if has_tool_use else 0,
                        None,
                    ),
                )
                stats["messages"] += 1
            except sqlite3.IntegrityError:
                pass

        # Process tool uses in assistant messages
        if obj_type == "assistant" and isinstance(msg, dict):
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue

                    tool_id = block.get("id", f"tu-{stats['tool_uses']}")
                    tool_name = block.get("name", "unknown")
                    tool_input = block.get("input", {})

                    # Extract file path (normalize to forward slashes)
                    file_path = tool_input.get("file_path") or tool_input.get(
                        "path"
                    )
                    if file_path:
                        file_path = file_path.replace("\\", "/")
                    command = tool_input.get("command")

                    # Classify activity
                    if tool_name == "Bash" and command:
                        activity = classify_bash(command)
                    elif tool_name in TOOL_ACTIVITY_MAP:
                        activity = TOOL_ACTIVITY_MAP[tool_name]
                    else:
                        activity = "other"

                    # Classify project
                    project = classify_project(file_path) or classify_project(
                        cwd
                    )

                    try:
                        conn.execute(
                            """INSERT OR IGNORE INTO tool_uses
                               (id, message_uuid, session_id, tool_name, timestamp,
                                file_path, command, activity_type, project, meta)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                tool_id,
                                uuid,
                                session_id,
                                tool_name,
                                ts,
                                file_path,
                                command[:500] if command else None,
                                activity,
                                project,
                                json.dumps(tool_input, default=str)[:2000],
                            ),
                        )
                        stats["tool_uses"] += 1
                    except sqlite3.IntegrityError:
                        pass

                    # Track files
                    if file_path:
                        fp_project = classify_project(file_path)
                        existing_file = conn.execute(
                            "SELECT * FROM files WHERE path = ?", (file_path,)
                        ).fetchone()
                        if existing_file:
                            updates = {"last_seen": ts}
                            if tool_name == "Read":
                                conn.execute(
                                    "UPDATE files SET last_seen=?, read_count=read_count+1 WHERE path=?",
                                    (ts, file_path),
                                )
                            elif tool_name == "Write":
                                conn.execute(
                                    "UPDATE files SET last_seen=?, write_count=write_count+1 WHERE path=?",
                                    (ts, file_path),
                                )
                            elif tool_name == "Edit":
                                conn.execute(
                                    "UPDATE files SET last_seen=?, edit_count=edit_count+1 WHERE path=?",
                                    (ts, file_path),
                                )
                            else:
                                conn.execute(
                                    "UPDATE files SET last_seen=? WHERE path=?",
                                    (ts, file_path),
                                )
                        else:
                            conn.execute(
                                """INSERT INTO files (path, project, first_seen, last_seen,
                                   read_count, write_count, edit_count)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (
                                    file_path,
                                    fp_project,
                                    ts,
                                    ts,
                                    1 if tool_name == "Read" else 0,
                                    1 if tool_name == "Write" else 0,
                                    1 if tool_name == "Edit" else 0,
                                ),
                            )
                            stats["files"] += 1

                    # Extract decisions
                    if tool_name == "AskUserQuestion":
                        decision = extract_decision(tool_input)
                        if decision:
                            conn.execute(
                                """INSERT INTO decisions
                                   (session_id, message_uuid, timestamp, question,
                                    answer, project, meta)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (
                                    session_id,
                                    uuid,
                                    ts,
                                    decision["question"],
                                    decision.get("answer"),
                                    project,
                                    json.dumps(decision),
                                ),
                            )
                            stats["decisions"] += 1

                    # Parse git operations
                    if tool_name == "Bash" and command:
                        git_op = parse_git_op(command)
                        if git_op:
                            conn.execute(
                                """INSERT INTO git_ops
                                   (session_id, tool_use_id, timestamp, operation,
                                    detail, project)
                                   VALUES (?, ?, ?, ?, ?, ?)""",
                                (
                                    session_id,
                                    tool_id,
                                    ts,
                                    git_op["operation"],
                                    git_op["detail"],
                                    project,
                                ),
                            )
                            stats["git_ops"] += 1

                    # Record activity
                    target = file_path or command[:100] if command else tool_name
                    conn.execute(
                        """INSERT INTO activities
                           (session_id, timestamp, type, target, project,
                            source_type, source_id, meta)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            session_id,
                            ts,
                            activity,
                            target,
                            project,
                            "tool_use",
                            tool_id,
                            None,
                        ),
                    )
                    stats["activities"] += 1

    conn.commit()
    return stats


# ── CLI Commands ──────────────────────────────────────────────


def _get_db_path():
    """Use DB_PATH if writable, else fall back to env var WATCHER_DB."""
    alt = os.environ.get("WATCHER_DB")
    if alt:
        return Path(alt)
    return DB_PATH


def cmd_parse(args):
    if not args:
        print("Usage: watcher.py parse <transcript.jsonl>")
        sys.exit(1)

    conn = init_db(_get_db_path())
    for path in args:
        print(f"Parsing: {path}")
        stats = parse_transcript(path, conn)
        print(f"  Messages:  {stats['messages']}")
        print(f"  Tool uses: {stats['tool_uses']}")
        print(f"  Files:     {stats['files']}")
        print(f"  Decisions: {stats['decisions']}")
        print(f"  Git ops:   {stats['git_ops']}")
        print(f"  Activities:{stats['activities']}")
    conn.close()


def cmd_sessions(args):
    conn = init_db(_get_db_path())
    rows = conn.execute(
        "SELECT id, cwd, started_at, message_count, tool_use_count FROM sessions ORDER BY started_at"
    ).fetchall()
    if not rows:
        print("No sessions in database.")
        return

    print(f"\n  {'ID':<40} {'CWD':<35} {'Started':<22} {'Msgs':>5} {'Tools':>5}")
    print(f"  {'-'*40} {'-'*35} {'-'*22} {'-'*5} {'-'*5}")
    for r in rows:
        sid = r["id"][:38]
        cwd_short = (r["cwd"] or "")[-33:]
        started = (r["started_at"] or "")[:19]
        print(
            f"  {sid:<40} {cwd_short:<35} {started:<22} {r['message_count']:>5} {r['tool_use_count']:>5}"
        )
    print()
    conn.close()


def cmd_activity(args):
    conn = init_db(_get_db_path())

    project_filter = None
    type_filter = None
    limit = 30

    i = 0
    while i < len(args):
        if args[i] == "--project" and i + 1 < len(args):
            project_filter = args[i + 1]
            i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            type_filter = args[i + 1]
            i += 2
        elif args[i] == "-n" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            i += 1

    query = "SELECT timestamp, type, target, project FROM activities WHERE 1=1"
    params = []
    if project_filter:
        query += " AND project = ?"
        params.append(project_filter)
    if type_filter:
        query += " AND type = ?"
        params.append(type_filter)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    if not rows:
        print("No activities found.")
        return

    print(f"\n  {'Timestamp':<22} {'Type':<15} {'Project':<18} {'Target'}")
    print(f"  {'-'*22} {'-'*15} {'-'*18} {'-'*40}")
    for r in reversed(rows):
        ts = (r["timestamp"] or "")[:19]
        target = (r["target"] or "")[:60]
        print(
            f"  {ts:<22} {r['type'] or '':<15} {r['project'] or '':<18} {target}"
        )
    print()
    conn.close()


def cmd_files(args):
    conn = init_db(_get_db_path())

    project_filter = None
    if "--project" in args:
        idx = args.index("--project")
        if idx + 1 < len(args):
            project_filter = args[idx + 1]

    query = "SELECT path, project, read_count, write_count, edit_count, first_seen, last_seen FROM files WHERE 1=1"
    params = []
    if project_filter:
        query += " AND project = ?"
        params.append(project_filter)
    query += " ORDER BY last_seen DESC"

    rows = conn.execute(query, params).fetchall()
    if not rows:
        print("No files tracked.")
        return

    print(
        f"\n  {'Project':<18} {'R':>3} {'W':>3} {'E':>3} {'Path'}"
    )
    print(
        f"  {'-'*18} {'-'*3} {'-'*3} {'-'*3} {'-'*50}"
    )
    for r in rows:
        p = (r["path"] or "")
        # Shorten path for display
        for name, roots in PROJECT_ROOTS.items():
            for root in roots:
                norm_root = root.replace("\\", "/")
                norm_p = p.replace("\\", "/")
                if norm_p.startswith(norm_root):
                    p = "..." + norm_p[len(norm_root):]
                    break
        print(
            f"  {r['project'] or '':<18} {r['read_count']:>3} {r['write_count']:>3} {r['edit_count']:>3} {p[:70]}"
        )
    print()
    conn.close()


def cmd_decisions(args):
    conn = init_db(_get_db_path())

    session_filter = None
    if "--session" in args:
        idx = args.index("--session")
        if idx + 1 < len(args):
            session_filter = args[idx + 1]

    query = "SELECT timestamp, question, answer, project FROM decisions WHERE 1=1"
    params = []
    if session_filter:
        query += " AND session_id = ?"
        params.append(session_filter)
    query += " ORDER BY timestamp"

    rows = conn.execute(query, params).fetchall()
    if not rows:
        print("No decisions recorded.")
        return

    print(f"\n  Decisions ({len(rows)}):\n")
    for r in rows:
        ts = (r["timestamp"] or "")[:19]
        q = (r["question"] or "")[:80]
        a = (r["answer"] or "")[:40]
        print(f"  [{ts}] {r['project'] or '?'}")
        print(f"    Q: {q}")
        print(f"    A: {a}")
        print()
    conn.close()


def cmd_stats(args):
    conn = init_db(_get_db_path())

    session_filter = None
    if "--session" in args:
        idx = args.index("--session")
        if idx + 1 < len(args):
            session_filter = args[idx + 1]

    # Overall stats
    session_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    message_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    tool_count = conn.execute("SELECT COUNT(*) FROM tool_uses").fetchone()[0]
    file_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    decision_count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    git_count = conn.execute("SELECT COUNT(*) FROM git_ops").fetchone()[0]

    print(f"\n  Watcher Database Stats")
    print(f"  {'='*40}")
    print(f"  Sessions:   {session_count}")
    print(f"  Messages:   {message_count}")
    print(f"  Tool uses:  {tool_count}")
    print(f"  Files:      {file_count}")
    print(f"  Decisions:  {decision_count}")
    print(f"  Git ops:    {git_count}")

    # Tool breakdown
    print(f"\n  Tool Usage Breakdown:")
    rows = conn.execute(
        "SELECT tool_name, COUNT(*) as c FROM tool_uses GROUP BY tool_name ORDER BY c DESC"
    ).fetchall()
    for r in rows:
        print(f"    {r['tool_name']:<30} {r['c']:>5}")

    # Project breakdown
    print(f"\n  Activity by Project:")
    rows = conn.execute(
        "SELECT project, COUNT(*) as c FROM activities WHERE project IS NOT NULL GROUP BY project ORDER BY c DESC"
    ).fetchall()
    for r in rows:
        print(f"    {r['project']:<30} {r['c']:>5}")

    # Activity type breakdown
    print(f"\n  Activity Types:")
    rows = conn.execute(
        "SELECT type, COUNT(*) as c FROM activities GROUP BY type ORDER BY c DESC"
    ).fetchall()
    for r in rows:
        print(f"    {r['type']:<30} {r['c']:>5}")

    print()
    conn.close()


def cmd_git_ops(args):
    conn = init_db(_get_db_path())

    session_filter = None
    if "--session" in args:
        idx = args.index("--session")
        if idx + 1 < len(args):
            session_filter = args[idx + 1]

    query = "SELECT timestamp, operation, detail, project FROM git_ops WHERE 1=1"
    params = []
    if session_filter:
        query += " AND session_id = ?"
        params.append(session_filter)
    query += " ORDER BY timestamp"

    rows = conn.execute(query, params).fetchall()
    if not rows:
        print("No git operations recorded.")
        return

    print(f"\n  Git Operations ({len(rows)}):\n")
    print(f"  {'Timestamp':<22} {'Op':<12} {'Project':<18} {'Detail'}")
    print(f"  {'-'*22} {'-'*12} {'-'*18} {'-'*40}")
    for r in rows:
        ts = (r["timestamp"] or "")[:19]
        detail = (r["detail"] or "")[:50]
        print(
            f"  {ts:<22} {r['operation']:<12} {r['project'] or '':<18} {detail}"
        )
    print()
    conn.close()


# ── Main ──────────────────────────────────────────────────────

COMMANDS = {
    "parse": cmd_parse,
    "sessions": cmd_sessions,
    "activity": cmd_activity,
    "files": cmd_files,
    "decisions": cmd_decisions,
    "stats": cmd_stats,
    "git-ops": cmd_git_ops,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
