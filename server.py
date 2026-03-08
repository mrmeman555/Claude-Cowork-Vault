#!/usr/bin/env python3
"""
ML OS Vault Browser — Local dev server
Serves the vault browser UI and API endpoints for vault data.
"""

import http.server
import json
import os
import sqlite3
import subprocess
import sys
import urllib.parse
from pathlib import Path

PORT = 3001
ROOT = Path(__file__).parent
VAULT_DIR = ROOT / "vault"
BENCH_DIR = ROOT / "bench"
INDEX_PATH = ROOT / ".mlos" / "index.json"
WATCHER_DB_PATH = ROOT / ".mlos" / "watcher.db"

# ── Whitelisted Operations ────────────────────────────────
# Only these commands can be executed from the web UI.
# Each entry: id → { label, description, command (list), category, icon }
OPERATIONS = {
    # ── Watcher ─────────────────────────────────
    "watcher-scan-dry": {
        "label": "Scan for Transcripts (preview)",
        "description": "Find new JSONL transcripts without parsing them",
        "command": [sys.executable, ".mlos/watcher/scan.py", "--dry-run"],
        "category": "watcher",
        "icon": "search",
    },
    "watcher-scan": {
        "label": "Scan & Parse New Transcripts",
        "description": "Find and ingest all new transcripts into the DB",
        "command": [sys.executable, ".mlos/watcher/scan.py"],
        "category": "watcher",
        "icon": "zap",
    },
    "watcher-stats": {
        "label": "Database Stats",
        "description": "Show current watcher DB counts",
        "command": [sys.executable, ".mlos/watcher.py", "stats"],
        "category": "watcher",
        "icon": "bar-chart",
    },
    "watcher-sessions": {
        "label": "List Sessions",
        "description": "Show all parsed transcript sessions",
        "command": [sys.executable, ".mlos/watcher.py", "sessions"],
        "category": "watcher",
        "icon": "list",
    },
    "watcher-activity": {
        "label": "Recent Activity (30)",
        "description": "Show the 30 most recent activity events",
        "command": [sys.executable, ".mlos/watcher.py", "activity", "-n", "30"],
        "category": "watcher",
        "icon": "activity",
    },
    "watcher-files": {
        "label": "Files Tracked",
        "description": "List all files observed across sessions",
        "command": [sys.executable, ".mlos/watcher.py", "files"],
        "category": "watcher",
        "icon": "file",
    },
    "watcher-decisions": {
        "label": "Decisions",
        "description": "Show all extracted decision points",
        "command": [sys.executable, ".mlos/watcher.py", "decisions"],
        "category": "watcher",
        "icon": "git-branch",
    },
    "watcher-git": {
        "label": "Git Operations",
        "description": "Show all parsed git commands",
        "command": [sys.executable, ".mlos/watcher.py", "git-ops"],
        "category": "watcher",
        "icon": "git-commit",
    },
    "watcher-sources": {
        "label": "Transcript Sources",
        "description": "Show configured scan locations and their status",
        "command": [sys.executable, ".mlos/watcher/scan.py", "--sources"],
        "category": "watcher",
        "icon": "folder",
    },
    # ── Vault ───────────────────────────────────
    "vault-scan": {
        "label": "Scan Inbox",
        "description": "Preview contents of io/inbox/",
        "command": [sys.executable, ".mlos/ingest.py", "scan"],
        "category": "vault",
        "icon": "inbox",
    },
    "vault-tasks": {
        "label": "Task List",
        "description": "Show all tasks across projects",
        "command": [sys.executable, ".mlos/ingest.py", "task", "list"],
        "category": "vault",
        "icon": "check-square",
    },
    "vault-check": {
        "label": "Check Index Integrity",
        "description": "Validate index.json against filesystem",
        "command": [sys.executable, ".mlos/ingest.py", "check"],
        "category": "vault",
        "icon": "shield",
    },
    "vault-view": {
        "label": "View Index",
        "description": "Show all indexed items",
        "command": [sys.executable, ".mlos/ingest.py", "view"],
        "category": "vault",
        "icon": "eye",
    },
    "vault-sync": {
        "label": "Sync Project State",
        "description": "Regenerate project-state.md from truth sources",
        "command": [sys.executable, ".mlos/ingest.py", "sync"],
        "category": "vault",
        "icon": "refresh-cw",
    },
    "vault-log": {
        "label": "Event Log (last 20)",
        "description": "Show recent vault events",
        "command": [sys.executable, ".mlos/ingest.py", "log", "-n", "20"],
        "category": "vault",
        "icon": "scroll",
    },
    # ── Git ─────────────────────────────────────
    "git-status": {
        "label": "Git Status",
        "description": "Show working tree status for this repo",
        "command": ["git", "status", "-sb"],
        "category": "git",
        "icon": "git-branch",
    },
    "git-log": {
        "label": "Git Log (last 10)",
        "description": "Show recent commits",
        "command": ["git", "log", "--oneline", "-10"],
        "category": "git",
        "icon": "git-commit",
    },
}


class VaultHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8",
    }

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/ops/run":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._serve_error(400, "Invalid JSON")
                return

            op_id = data.get("id")
            if not op_id or op_id not in OPERATIONS:
                self._serve_error(400, f"Unknown operation: {op_id}")
                return

            op = OPERATIONS[op_id]
            try:
                result = subprocess.run(
                    op["command"],
                    capture_output=True,
                    text=True,
                    cwd=str(ROOT),
                    timeout=30,
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                )
                self._serve_json({
                    "id": op_id,
                    "ok": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "code": result.returncode,
                })
            except subprocess.TimeoutExpired:
                self._serve_json({
                    "id": op_id,
                    "ok": False,
                    "stdout": "",
                    "stderr": "Command timed out (30s limit)",
                    "code": -1,
                })
            except Exception as e:
                self._serve_json({
                    "id": op_id,
                    "ok": False,
                    "stdout": "",
                    "stderr": str(e),
                    "code": -1,
                })
        else:
            self._serve_error(404, "Not found")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/ops/list":
            # Return the operation registry for the UI
            ops = []
            for op_id, op in OPERATIONS.items():
                ops.append({
                    "id": op_id,
                    "label": op["label"],
                    "description": op["description"],
                    "category": op["category"],
                    "icon": op.get("icon", "terminal"),
                })
            self._serve_json(ops)
        elif path == "/api/index":
            self._serve_json(self._load_index())
        elif path == "/api/projects":
            self._serve_json(self._get_projects())
        elif path == "/api/file":
            project = query.get("project", [None])[0]
            filename = query.get("filename", [None])[0]
            subpath = query.get("subpath", [None])[0]
            if project and filename:
                self._serve_file_content(project, filename, subpath)
            else:
                self._serve_error(400, "Missing project or filename parameter")
        elif path == "/api/tree":
            self._serve_json(self._get_tree())
        elif path == "/api/tasks":
            project = query.get("project", [None])[0]
            self._serve_json(self._get_tasks(project))
        # ── Watcher API endpoints ─────────────────────
        elif path == "/api/sessions":
            self._serve_json(self._get_sessions())
        elif path == "/api/watcher/stats":
            self._serve_json(self._watcher_stats())
        elif path == "/api/watcher/sessions":
            self._serve_json(self._watcher_sessions())
        elif path == "/api/watcher/activity":
            project = query.get("project", [None])[0]
            activity_type = query.get("type", [None])[0]
            limit = int(query.get("limit", [100])[0])
            self._serve_json(self._watcher_activity(project, activity_type, limit))
        elif path == "/api/watcher/files":
            project = query.get("project", [None])[0]
            self._serve_json(self._watcher_files(project))
        elif path == "/api/watcher/decisions":
            session_id = query.get("session", [None])[0]
            self._serve_json(self._watcher_decisions(session_id))
        elif path == "/api/watcher/git-ops":
            session_id = query.get("session", [None])[0]
            self._serve_json(self._watcher_git_ops(session_id))
        elif path == "/api/watcher/tool-breakdown":
            self._serve_json(self._watcher_tool_breakdown())
        elif path == "/api/watcher/project-breakdown":
            self._serve_json(self._watcher_project_breakdown())
        else:
            super().do_GET()

    def _load_index(self):
        if INDEX_PATH.exists():
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"version": "1.0", "last_updated": None, "items": []}

    def _get_projects(self):
        index = self._load_index()
        projects = {}
        for item in index.get("items", []):
            p = item["project"]
            if p not in projects:
                projects[p] = {"name": p, "count": 0, "total_size": 0, "types": set()}
            projects[p]["count"] += 1
            projects[p]["total_size"] += item.get("size", 0)
            projects[p]["types"].add(item.get("type", "unknown"))

        # Also include vault dirs that exist but have no indexed items
        if VAULT_DIR.exists():
            for d in VAULT_DIR.iterdir():
                if d.is_dir() and d.name not in projects and not d.name.startswith("."):
                    projects[d.name] = {"name": d.name, "count": 0, "total_size": 0, "types": set()}

        # Convert sets to lists for JSON
        result = []
        for p in sorted(projects.values(), key=lambda x: x["name"]):
            p["types"] = sorted(p["types"])
            result.append(p)
        return result

    def _get_tree(self):
        """Full vault tree: projects -> files, including unindexed files."""
        index = self._load_index()
        indexed = {}
        for item in index.get("items", []):
            key = f"{item['project']}/{item.get('subpath', '')}/{item['filename']}".replace("//", "/")
            indexed[key] = item

        tree = {}
        if VAULT_DIR.exists():
            for project_dir in sorted(VAULT_DIR.iterdir()):
                if not project_dir.is_dir() or project_dir.name.startswith("."):
                    continue
                pname = project_dir.name
                tree[pname] = []
                for dirpath, dirnames, filenames in os.walk(project_dir):
                    dirnames[:] = [d for d in dirnames if not d.startswith(".")]
                    for fname in sorted(filenames):
                        if fname in (".gitkeep", ".DS_Store", "Thumbs.db", "tasks.json"):
                            continue
                        fpath = Path(dirpath) / fname
                        rel = fpath.relative_to(project_dir)
                        key = f"{pname}/{rel}".replace("\\", "/")
                        if key in indexed:
                            entry = dict(indexed[key])
                            entry["on_disk"] = True
                            tree[pname].append(entry)
                        else:
                            tree[pname].append({
                                "filename": fname,
                                "subpath": str(rel.parent).replace("\\", "/") if rel.parent != Path(".") else None,
                                "type": fpath.suffix.lstrip(".") or "file",
                                "size": fpath.stat().st_size,
                                "on_disk": True,
                                "indexed": False,
                            })
        return tree

    def _get_tasks(self, project=None):
        """Load tasks from one or all projects."""
        all_tasks = []
        if project:
            projects = [project]
        else:
            projects = [d.name for d in VAULT_DIR.iterdir()
                        if d.is_dir() and not d.name.startswith(".")]
        for proj in sorted(projects):
            tasks_path = VAULT_DIR / proj / "tasks.json"
            if tasks_path.exists():
                try:
                    with open(tasks_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for task in data.get("tasks", []):
                        task["project"] = proj
                        all_tasks.append(task)
                except (json.JSONDecodeError, IOError):
                    pass
        return all_tasks

    # ── Sessions (git branch queries) ─────────────────────

    def _get_sessions(self):
        """Query git for open and merged session/* branches on OpenClaw_Claude."""
        openclaw_dir = Path("C:/Users/Erinh/Desktop/OpenClaw_Claude")
        result = {"open": [], "merged": []}

        if not openclaw_dir.exists():
            return result

        try:
            # Find all local session/* branches
            branch_out = subprocess.run(
                ["git", "for-each-ref", "--format=%(refname:short)\t%(creatordate:iso8601)", "refs/heads/session/"],
                capture_output=True, text=True, cwd=str(openclaw_dir), timeout=10
            )
            open_branches = set()
            for line in branch_out.stdout.strip().splitlines():
                if not line:
                    continue
                parts = line.split("\t", 1)
                branch = parts[0]
                created = parts[1] if len(parts) > 1 else ""
                open_branches.add(branch)

                # Extract project from branch name: session/{project}/{date}/{id}
                branch_parts = branch.split("/")
                project = branch_parts[1] if len(branch_parts) > 1 else "unknown"
                branch_date = branch_parts[2] if len(branch_parts) > 2 else ""

                # Count chats from .session-chats.json if it exists
                chats = 0
                chats_file = VAULT_DIR / project / ".session-chats.json"
                if chats_file.exists():
                    try:
                        with open(chats_file) as f:
                            chats = len(json.load(f))
                    except (json.JSONDecodeError, IOError):
                        pass

                result["open"].append({
                    "branch": branch,
                    "project": project,
                    "created": branch_date or created[:10],
                    "chats": chats,
                    "status": "open",
                })

            # Find merged session branches from git log
            merge_out = subprocess.run(
                ["git", "log", "--oneline", "--all", "--grep=session:", "--format=%s\t%ai"],
                capture_output=True, text=True, cwd=str(openclaw_dir), timeout=10
            )
            seen_merged = set()
            for line in merge_out.stdout.strip().splitlines():
                if not line or "session:" not in line:
                    continue
                parts = line.split("\t", 1)
                subject = parts[0]
                merge_date = parts[1][:10] if len(parts) > 1 else ""

                # Extract project from commit message "session: {project} {date} — ..."
                msg_parts = subject.replace("session:", "").strip().split()
                project = msg_parts[0] if msg_parts else "unknown"

                if subject not in seen_merged:
                    seen_merged.add(subject)
                    result["merged"].append({
                        "branch": subject,
                        "project": project,
                        "merged": merge_date,
                        "status": "merged",
                    })

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return result

    # ── Watcher DB helpers ─────────────────────────────────

    def _watcher_db(self):
        """Open a read-only connection to the watcher DB. Returns None if not available."""
        if not WATCHER_DB_PATH.exists():
            return None
        conn = sqlite3.connect(str(WATCHER_DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    def _watcher_stats(self):
        conn = self._watcher_db()
        if not conn:
            return {"available": False}
        try:
            stats = {"available": True}
            for table in ["sessions", "messages", "tool_uses", "files", "decisions", "git_ops", "activities"]:
                try:
                    stats[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                except sqlite3.OperationalError:
                    stats[table] = 0
            return stats
        except Exception:
            return {"available": False}
        finally:
            conn.close()

    def _watcher_sessions(self):
        conn = self._watcher_db()
        if not conn:
            return []
        try:
            rows = conn.execute(
                "SELECT id, transcript_path, cwd, git_branch, started_at, ended_at, message_count, tool_use_count, meta FROM sessions ORDER BY started_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _watcher_activity(self, project=None, activity_type=None, limit=100):
        conn = self._watcher_db()
        if not conn:
            return []
        try:
            query = "SELECT id, session_id, timestamp, type, target, project, source_type, source_id FROM activities WHERE 1=1"
            params = []
            if project:
                query += " AND project = ?"
                params.append(project)
            if activity_type:
                query += " AND type = ?"
                params.append(activity_type)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _watcher_files(self, project=None):
        conn = self._watcher_db()
        if not conn:
            return []
        try:
            query = "SELECT path, project, first_seen, last_seen, read_count, write_count, edit_count FROM files WHERE 1=1"
            params = []
            if project:
                query += " AND project = ?"
                params.append(project)
            query += " ORDER BY last_seen DESC"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _watcher_decisions(self, session_id=None):
        conn = self._watcher_db()
        if not conn:
            return []
        try:
            query = "SELECT id, session_id, message_uuid, timestamp, question, answer, project, meta FROM decisions WHERE 1=1"
            params = []
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            query += " ORDER BY timestamp"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _watcher_git_ops(self, session_id=None):
        conn = self._watcher_db()
        if not conn:
            return []
        try:
            query = "SELECT id, session_id, tool_use_id, timestamp, operation, detail, project FROM git_ops WHERE 1=1"
            params = []
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            query += " ORDER BY timestamp"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _watcher_tool_breakdown(self):
        conn = self._watcher_db()
        if not conn:
            return []
        try:
            rows = conn.execute(
                "SELECT tool_name, COUNT(*) as count FROM tool_uses GROUP BY tool_name ORDER BY count DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _watcher_project_breakdown(self):
        conn = self._watcher_db()
        if not conn:
            return []
        try:
            rows = conn.execute(
                "SELECT project, COUNT(*) as count, "
                "SUM(CASE WHEN type='create' THEN 1 ELSE 0 END) as creates, "
                "SUM(CASE WHEN type='read' THEN 1 ELSE 0 END) as reads, "
                "SUM(CASE WHEN type='modify' THEN 1 ELSE 0 END) as modifies, "
                "SUM(CASE WHEN type IN ('execute','run','install') THEN 1 ELSE 0 END) as executes, "
                "SUM(CASE WHEN type LIKE 'git_%' THEN 1 ELSE 0 END) as git_ops "
                "FROM activities WHERE project IS NOT NULL GROUP BY project ORDER BY count DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def _serve_file_content(self, project, filename, subpath=None):
        if subpath:
            fpath = VAULT_DIR / project / subpath / filename
        else:
            fpath = VAULT_DIR / project / filename

        # Security: ensure path stays within vault
        try:
            fpath.resolve().relative_to(VAULT_DIR.resolve())
        except ValueError:
            self._serve_error(403, "Path traversal denied")
            return

        if not fpath.exists():
            self._serve_error(404, f"File not found: {project}/{filename}")
            return

        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
            self._serve_json({"filename": filename, "project": project, "content": content})
        except Exception as e:
            self._serve_json({"filename": filename, "project": project, "content": f"[Binary or unreadable: {e}]"})

    def _serve_json(self, data):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_error(self, code, message):
        body = json.dumps({"error": message}).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        if "/api/" not in str(args[0]):
            super().log_message(format, *args)


if __name__ == "__main__":
    os.chdir(ROOT)
    print(f"ML OS Vault Browser — http://localhost:{PORT}")
    print(f"Vault: {VAULT_DIR}")
    print(f"Index: {INDEX_PATH}")
    server = http.server.HTTPServer(("", PORT), VaultHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")
