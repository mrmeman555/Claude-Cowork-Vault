#!/usr/bin/env python3
"""
ML OS Vault Browser — Local dev server
Serves the vault browser UI and API endpoints for vault data.
"""

import http.server
import json
import os
import sys
import urllib.parse
from pathlib import Path

PORT = 3001
ROOT = Path(__file__).parent
VAULT_DIR = ROOT / "vault"
BENCH_DIR = ROOT / "bench"
INDEX_PATH = ROOT / ".mlos" / "index.json"


class VaultHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8",
    }

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/index":
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
