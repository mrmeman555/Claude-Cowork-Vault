#!/usr/bin/env python3
"""
ML OS — Vault Ingest Pipeline

Moves files from io/inbox/ into vault/{project}/, auto-populates index.json
with minimal metadata, and provides query/validation tools.

Usage:
  python .mlos/ingest.py scan [path]                 Preview inbox contents (default: io/inbox/)
  python .mlos/ingest.py add <path> --project <name> Ingest file or folder into vault
  python .mlos/ingest.py write --project <name> --filename <name> [--title <t>]  Write content to vault
  python .mlos/ingest.py view [--project <name>] [--type <ext>]  Query the index
  python .mlos/ingest.py check                       Validate index vs filesystem
  python .mlos/ingest.py export --project <name>     Render index as markdown
  python .mlos/ingest.py sync [--dry-run]            Regenerate project-state.md from truth sources
  python .mlos/ingest.py log [--action <type>] [-n N] View event log (most recent first)
  python .mlos/ingest.py task add --project <name> --title "..." [--priority ...] [--type ...] [--tags a,b] [--notes "..."]
  python .mlos/ingest.py task list [--project <name>] [--status ...] [--type ...] [--tag <tag>]
  python .mlos/ingest.py task update <id> [--status ...] [--priority ...] [--title "..."] [--notes "..."]
  python .mlos/ingest.py task done <id> [--project <name>]

Options:
  --flatten       When ingesting a folder, flatten all files (prefix with folder name)
  --preserve      When ingesting a folder, keep subfolder structure in vault
  --dry-run       Show what would happen without moving files or writing index
  --stdin         (write command) Read file content from stdin instead of --content
"""

import sys
import os
import io
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
MLOS_DIR = ROOT / ".mlos"
INDEX_PATH = MLOS_DIR / "index.json"
VAULT_DIR = ROOT / "vault"
INBOX_DIR = ROOT / "io" / "inbox"

SKIP_FILES = {".DS_Store", "Thumbs.db", ".gitignore", ".gitkeep", "tasks.json"}
SKIP_DIRS = {".git", "__pycache__", ".specstory", "node_modules"}

# ── Colors ────────────────────────────────────────────────────

G = "\033[32m"; C = "\033[36m"; Y = "\033[33m"; M = "\033[35m"
B = "\033[1m"; D = "\033[2m"; R = "\033[0m"; RED = "\033[31m"

# ── File Types (shared with moc.py) ──────────────────────────

FILE_TYPES = {
    ".md": "markdown", ".txt": "text", ".py": "python",
    ".js": "javascript", ".ts": "typescript", ".json": "json",
    ".yaml": "yaml", ".yml": "yaml", ".pdf": "pdf",
    ".docx": "docx", ".doc": "doc", ".csv": "csv",
    ".html": "html", ".css": "css", ".sh": "shell",
    ".ipynb": "notebook", ".png": "image", ".jpg": "image",
    ".jpeg": "image", ".gif": "image", ".svg": "image",
    ".mp3": "audio", ".wav": "audio", ".mp4": "video",
    ".zip": "archive", ".tar": "archive", ".gz": "archive",
    ".xlsx": "excel", ".xls": "excel", ".pptx": "powerpoint",
}


def file_type(path):
    return FILE_TYPES.get(Path(path).suffix.lower(), Path(path).suffix.lower().lstrip(".") or "file")


def human_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ── Index I/O ─────────────────────────────────────────────────

def load_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "last_updated": None, "items": []}


def save_index(index):
    index["last_updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def generate_id(filename):
    """8-char hex hash from filename + current timestamp."""
    raw = f"{filename}:{datetime.now().isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def index_has_file(index, filename, project):
    """Check if a file is already indexed in a project."""
    for item in index["items"]:
        if item["filename"] == filename and item["project"] == project:
            return True
    return False


# ── Event Log ────────────────────────────────────────────────

EVENT_LOG_PATH = MLOS_DIR / "events.jsonl"

def log_event(action, **kwargs):
    """Append a structured event to events.jsonl.

    Actions: add, write, sync, check, delete
    All events get a timestamp and action field automatically.
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "action": action,
    }
    event.update(kwargs)
    with open(EVENT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# ── Task I/O ─────────────────────────────────────────────────

def load_tasks(project):
    """Load tasks.json for a project. Returns empty structure if not found."""
    tasks_path = VAULT_DIR / project / "tasks.json"
    if tasks_path.exists():
        with open(tasks_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "1.0", "last_updated": None, "tasks": []}


def save_tasks(project, tasks_data):
    """Save tasks.json for a project. Auto-timestamps."""
    tasks_path = VAULT_DIR / project / "tasks.json"
    tasks_data["last_updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tasks_path, "w", encoding="utf-8") as f:
        json.dump(tasks_data, f, indent=2, ensure_ascii=False)


def generate_task_id(title):
    """Generate a task ID: t- prefix + 6-char hex hash."""
    raw = f"{title}:{datetime.now().isoformat()}"
    return "t-" + hashlib.sha256(raw.encode()).hexdigest()[:6]


def _find_task(task_id, project=None):
    """Find a task by ID across one or all projects.
    Returns (project_name, task_dict, tasks_data) or (None, None, None).
    """
    if project:
        projects = [project]
    else:
        projects = [d.name for d in VAULT_DIR.iterdir()
                    if d.is_dir() and not d.name.startswith(".")]
    for proj in projects:
        data = load_tasks(proj)
        for task in data.get("tasks", []):
            if task["id"] == task_id:
                return proj, task, data
    return None, None, None


# ── Title Extraction (from moc.py) ───────────────────────────

def extract_title(path):
    """Extract the first meaningful heading or description from a file."""
    path = Path(path)
    try:
        if path.suffix.lower() == ".md":
            return _title_markdown(path)
        elif path.suffix.lower() == ".py":
            return _title_python(path)
        elif path.suffix.lower() == ".txt":
            return _title_text(path)
        elif path.suffix.lower() == ".docx":
            return _title_docx(path)
        elif path.suffix.lower() in (".yaml", ".yml"):
            return _title_yaml(path)
    except Exception:
        pass
    # Fallback: clean filename
    return path.stem.replace("_", " ").replace("-", " ")


def _title_markdown(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()[:120]
    return path.stem


def _title_python(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(500)
    for marker in ['"""', "'''"]:
        if marker in content:
            start = content.index(marker) + 3
            end = content.find(marker, start)
            if end > start:
                return content[start:end].strip().split("\n")[0][:120]
    return path.stem


def _title_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                return line.strip()[:120]
    return path.stem


def _title_docx(path):
    name = path.stem
    if "Lab" in name:
        parts = name.split("Lab")
        if len(parts) > 1:
            return f"Lab {parts[-1]}"
    return name.replace("_", " ").replace("-", " ")


def _title_yaml(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()[:120]
    return path.stem


# ── SCAN ──────────────────────────────────────────────────────

def cmd_scan(args):
    target = Path(args[0]).resolve() if args else INBOX_DIR.resolve()

    if not target.exists():
        print(f"  {RED}Error: Path not found: {target}{R}")
        return

    if not str(target.resolve()).startswith(str(INBOX_DIR.resolve())):
        print(f"  {RED}Error: Can only scan inside io/inbox/{R}")
        print(f"  {D}Drop files in io/inbox/ first, then scan.{R}")
        return

    files = []
    dirs_seen = set()
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        current = Path(dirpath)
        for fname in sorted(filenames):
            if fname in SKIP_FILES:
                continue
            fpath = current / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                size = 0
            rel = fpath.relative_to(target)
            parent = str(rel.parent)
            if parent != ".":
                dirs_seen.add(parent)
            files.append({
                "path": str(rel),
                "name": fname,
                "parent": parent,
                "type": file_type(fpath),
                "size": size,
                "title": extract_title(fpath),
            })

    if not files:
        print(f"\n  {D}Inbox is empty. Drop files in io/inbox/ to get started.{R}\n")
        return

    # Summary
    print(f"\n  {G}{B}Inbox Scan — {target.name}/{R}")
    print(f"  {D}Path: {target}{R}")
    print(f"  {D}Files: {len(files)} | Folders: {len(dirs_seen)}{R}\n")

    # Group by parent folder
    if dirs_seen:
        # Show structure
        print(f"  {C}Structure detected:{R}")
        print(f"  {D}./{R} ({sum(1 for f in files if f['parent'] == '.')} files)")
        for d in sorted(dirs_seen):
            count = sum(1 for f in files if f['parent'] == d or f['parent'].startswith(d + "/") or f['parent'].startswith(d + "\\"))
            print(f"  {D}  {d}/{R} ({count} files)")
        print()

    # File listing
    print(f"  {'File':<45} {'Type':<10} {'Size':<10} Title")
    print(f"  {'-'*45} {'-'*10} {'-'*10} {'-'*30}")
    for f in files:
        display_path = f["path"] if f["parent"] != "." else f["name"]
        title = (f["title"] or "")[:35]
        print(f"  {display_path:<45} {f['type']:<10} {human_size(f['size']):<10} {title}")

    print(f"\n  {Y}To ingest:{R}")
    print(f"  python .mlos/ingest.py add {target.relative_to(ROOT)} --project <name>")
    if dirs_seen:
        print(f"\n  {D}This folder has subfolders. You'll be asked to --flatten or --preserve.{R}")
    print()


# ── ADD ───────────────────────────────────────────────────────

def cmd_add(args):
    # Parse arguments
    path_arg = None
    project = None
    flatten = None  # None = ask, True = flatten, False = preserve
    dry_run = False

    i = 0
    while i < len(args):
        if args[i] == "--project":
            project = args[i + 1]
            i += 2
        elif args[i] == "--flatten":
            flatten = True
            i += 1
        elif args[i] == "--preserve":
            flatten = False
            i += 1
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            path_arg = args[i]
            i += 1

    if not path_arg or not project:
        print("  Usage: python .mlos/ingest.py add <path> --project <name>")
        print("  Options: --flatten | --preserve | --dry-run")
        return

    source = Path(path_arg).resolve()
    if not source.exists():
        # Try relative to ROOT
        source = (ROOT / path_arg).resolve()
    if not source.exists():
        print(f"  {RED}Error: Path not found: {path_arg}{R}")
        return

    # Verify source is inside inbox
    if not str(source).startswith(str(INBOX_DIR.resolve())):
        print(f"  {RED}Error: Source must be inside io/inbox/{R}")
        print(f"  {D}Move or copy files to io/inbox/ first.{R}")
        return

    # Collect files
    if source.is_file():
        files_to_ingest = [source]
        has_subdirs = False
    else:
        files_to_ingest = []
        has_subdirs = False
        for dirpath, dirnames, filenames in os.walk(source):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            if dirnames and Path(dirpath) == source:
                has_subdirs = True
            for fname in sorted(filenames):
                if fname in SKIP_FILES:
                    continue
                files_to_ingest.append(Path(dirpath) / fname)

    if not files_to_ingest:
        print(f"  {D}No files to ingest.{R}")
        return

    # Ask about nesting strategy if needed
    if has_subdirs and flatten is None:
        print(f"\n  {Y}This folder has subfolders:{R}")
        for dirpath, dirnames, _ in os.walk(source):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            rel = Path(dirpath).relative_to(source)
            if str(rel) != ".":
                count = len([f for f in (Path(dirpath)).iterdir() if f.is_file() and f.name not in SKIP_FILES])
                print(f"    {rel}/ ({count} files)")
        print()
        print(f"  {C}How should these be organized in the vault?{R}")
        print(f"  [1] {B}Flatten{R} — All files go to vault/{project}/ with folder prefix")
        print(f"      e.g., ryanliupie/notes/ch1.md → ryanliupie_notes_ch1.md")
        print(f"  [2] {B}Preserve{R} — Keep folder structure inside vault/{project}/")
        print(f"      e.g., ryanliupie/notes/ch1.md → vault/{project}/ryanliupie/notes/ch1.md")
        print()
        choice = input(f"  Choice [1/2]: ").strip()
        if choice == "1":
            flatten = True
        elif choice == "2":
            flatten = False
        else:
            print(f"  {D}Cancelled.{R}")
            return

    # Ensure vault project directory exists
    vault_project = VAULT_DIR / project
    if not dry_run:
        vault_project.mkdir(parents=True, exist_ok=True)

    # Load index
    index = load_index()

    # Process each file
    ingested = []
    skipped = []
    collisions = []

    print(f"\n  {G}{B}Ingesting into vault/{project}/{R}")
    if dry_run:
        print(f"  {Y}(DRY RUN — no files will be moved){R}")
    print()

    for fpath in files_to_ingest:
        # Determine destination filename
        if source.is_file():
            dest_name = fpath.name
            rel_path = None
        else:
            rel = fpath.relative_to(source)
            if flatten or not has_subdirs:
                # Flatten: join all parent dirs into filename prefix
                if rel.parent != Path("."):
                    prefix = str(rel.parent).replace("/", "_").replace("\\", "_")
                    dest_name = f"{prefix}_{rel.name}"
                else:
                    dest_name = rel.name
                rel_path = None
            else:
                # Preserve: keep relative path
                dest_name = rel.name
                rel_path = str(rel.parent).replace("\\", "/") if rel.parent != Path(".") else None

        # Determine destination path
        if rel_path:
            dest_dir = vault_project / rel_path
            dest = dest_dir / dest_name
        else:
            dest_dir = vault_project
            dest = vault_project / dest_name

        # Check collision
        if dest.exists() or index_has_file(index, dest_name, project):
            # Auto-rename: append _2, _3, etc.
            stem = Path(dest_name).stem
            suffix = Path(dest_name).suffix
            counter = 2
            while True:
                new_name = f"{stem}_{counter}{suffix}"
                new_dest = dest_dir / new_name
                if not new_dest.exists() and not index_has_file(index, new_name, project):
                    collisions.append((dest_name, new_name))
                    dest_name = new_name
                    dest = new_dest
                    break
                counter += 1

        # Build index entry
        try:
            size = fpath.stat().st_size
        except OSError:
            size = 0

        entry = {
            "id": generate_id(dest_name),
            "filename": dest_name,
            "type": file_type(fpath),
            "size": size,
            "title": extract_title(fpath),
            "ingested": datetime.now().strftime("%Y-%m-%d"),
            "project": project,
        }

        # Store relative path in index only if structure is preserved
        if rel_path:
            entry["subpath"] = rel_path

        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(fpath), str(dest))
            index["items"].append(entry)
            ingested.append(entry)
        else:
            ingested.append(entry)

        # Print progress
        status = f"{G}+{R}" if not dry_run else f"{Y}~{R}"
        display = f"{entry.get('subpath', '')}/{dest_name}" if rel_path else dest_name
        print(f"  {status} {display:<50} {entry['type']:<10} {human_size(size)}")

    # Clean up empty directories in inbox (only if not dry run)
    if not dry_run and source.is_dir():
        _cleanup_empty_dirs(source)

    # Save index
    if not dry_run and ingested:
        save_index(index)
        # Log events
        for entry in ingested:
            log_event("add", project=project, filename=entry["filename"],
                      item_id=entry["id"], type=entry["type"], size=entry["size"])

    # Summary
    print()
    if collisions:
        print(f"  {Y}Renamed {len(collisions)} file(s) to avoid collisions:{R}")
        for old, new in collisions:
            print(f"    {old} → {new}")
        print()

    action = "Would ingest" if dry_run else "Ingested"
    print(f"  {G}{B}{action} {len(ingested)} file(s) into vault/{project}/{R}")
    if skipped:
        print(f"  {Y}Skipped {len(skipped)} file(s) (already indexed){R}")
    print()

    # Auto integrity check
    if not dry_run and ingested:
        _post_op_check()


def _cleanup_empty_dirs(path):
    """Remove empty directories bottom-up."""
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        current = Path(dirpath)
        if current == INBOX_DIR:
            continue
        try:
            remaining = list(current.iterdir())
            if not remaining:
                current.rmdir()
        except OSError:
            pass


# ── VIEW ──────────────────────────────────────────────────────

def cmd_view(args):
    index = load_index()
    items = index.get("items", [])

    if not items:
        print(f"\n  {D}Index is empty. Ingest some files first.{R}\n")
        return

    # Parse filters
    project_filter = None
    type_filter = None
    i = 0
    while i < len(args):
        if args[i] == "--project":
            project_filter = args[i + 1]
            i += 2
        elif args[i] == "--type":
            type_filter = args[i + 1]
            i += 2
        else:
            i += 1

    # Apply filters
    filtered = items
    if project_filter:
        filtered = [it for it in filtered if it["project"] == project_filter]
    if type_filter:
        filtered = [it for it in filtered if it["type"] == type_filter]

    if not filtered:
        print(f"\n  {D}No items match the filter.{R}\n")
        return

    # Group by project
    by_project = {}
    for it in filtered:
        by_project.setdefault(it["project"], []).append(it)

    print(f"\n  {G}{B}Vault Index — {len(filtered)} item(s){R}")
    if project_filter:
        print(f"  {D}Project: {project_filter}{R}")
    if type_filter:
        print(f"  {D}Type: {type_filter}{R}")
    print()

    for proj, proj_items in sorted(by_project.items()):
        print(f"  {C}{B}{proj}/{R} ({len(proj_items)} items)")
        print(f"  {'ID':<10} {'Filename':<45} {'Type':<10} {'Size':<10} Title")
        print(f"  {'-'*10} {'-'*45} {'-'*10} {'-'*10} {'-'*30}")
        for it in sorted(proj_items, key=lambda x: x["filename"]):
            title = (it.get("title") or "")[:30]
            sid = it["id"]
            fname = it["filename"]
            if it.get("subpath"):
                fname = f"{it['subpath']}/{fname}"
            print(f"  {sid:<10} {fname:<45} {it['type']:<10} {human_size(it['size']):<10} {title}")
        print()


# ── CHECK (Validate) ─────────────────────────────────────────

def _run_check():
    """Core integrity check. Returns (missing, orphans, duplicates, items_count)."""
    index = load_index()
    items = index.get("items", [])

    missing = []
    orphans = []
    duplicates = []

    if not items:
        return missing, orphans, duplicates, 0

    # Check index -> filesystem
    seen = set()
    for item in items:
        key = (item["filename"], item["project"])
        if key in seen:
            duplicates.append(item)
        seen.add(key)

        subpath = item.get("subpath")
        if subpath:
            expected = VAULT_DIR / item["project"] / subpath / item["filename"]
        else:
            expected = VAULT_DIR / item["project"] / item["filename"]
        if not expected.exists():
            missing.append(item)

    # Check filesystem -> index
    indexed_files = set()
    for item in items:
        subpath = item.get("subpath")
        if subpath:
            indexed_files.add(str(Path(item["project"]) / subpath / item["filename"]))
        else:
            indexed_files.add(str(Path(item["project"]) / item["filename"]))

    if VAULT_DIR.exists():
        for dirpath, dirnames, filenames in os.walk(VAULT_DIR):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                if fname in SKIP_FILES or fname == ".gitkeep":
                    continue
                fpath = Path(dirpath) / fname
                rel = str(fpath.relative_to(VAULT_DIR))
                if rel.replace("\\", "/") not in {f.replace("\\", "/") for f in indexed_files}:
                    orphans.append(rel)

    return missing, orphans, duplicates, len(items)


def _post_op_check():
    """Silent integrity check after add/write. Only prints if issues found."""
    missing, orphans, duplicates, count = _run_check()
    if missing or orphans or duplicates:
        issues = []
        if missing:
            issues.append(f"{len(missing)} missing")
        if orphans:
            issues.append(f"{len(orphans)} orphans")
        if duplicates:
            issues.append(f"{len(duplicates)} duplicates")
        print(f"  {Y}Integrity warning: {', '.join(issues)}. Run 'check' for details.{R}")
        log_event("check", result="issues", items=count,
                  missing=len(missing), orphans=len(orphans), duplicates=len(duplicates),
                  trigger="auto")


def cmd_check(args):
    missing, orphans, duplicates, count = _run_check()

    if count == 0:
        print(f"\n  {D}Index is empty. Nothing to check.{R}\n")
        return

    # Report
    print(f"\n  {G}{B}Vault Integrity Check{R}")
    print(f"  {D}Index: {count} items | Vault: {VAULT_DIR}{R}\n")

    if not missing and not orphans and not duplicates:
        log_event("check", result="ok", items=count)
        print(f"  {G}All clear. Index matches filesystem.{R}\n")
        return

    log_event("check", result="issues", items=count,
              missing=len(missing), orphans=len(orphans), duplicates=len(duplicates))

    if missing:
        print(f"  {RED}{B}Missing from disk ({len(missing)}):{R}")
        for item in missing:
            print(f"    {item['project']}/{item['filename']} (id: {item['id']})")
        print()

    if orphans:
        print(f"  {Y}{B}Orphan files — on disk but not in index ({len(orphans)}):{R}")
        for o in orphans:
            print(f"    {o}")
        print()

    if duplicates:
        print(f"  {RED}{B}Duplicate index entries ({len(duplicates)}):{R}")
        for item in duplicates:
            print(f"    {item['filename']} in {item['project']} (id: {item['id']})")
        print()


# ── EXPORT ────────────────────────────────────────────────────

def cmd_export(args):
    index = load_index()
    items = index.get("items", [])

    project = None
    i = 0
    while i < len(args):
        if args[i] == "--project":
            project = args[i + 1]
            i += 2
        else:
            i += 1

    if not project:
        print("  Usage: python .mlos/ingest.py export --project <name>")
        return

    filtered = [it for it in items if it["project"] == project]
    if not filtered:
        print(f"  {D}No items in project '{project}'.{R}")
        return

    # Render markdown
    lines = []
    lines.append(f"# Index — {project}")
    lines.append(f"")
    lines.append(f"> Auto-generated from .mlos/index.json")
    lines.append(f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> Items: {len(filtered)}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"| ID | Filename | Type | Size | Title |")
    lines.append(f"|-----|----------|------|------|-------|")
    for it in sorted(filtered, key=lambda x: x["filename"]):
        fname = it["filename"]
        if it.get("subpath"):
            fname = f"{it['subpath']}/{fname}"
        title = it.get("title", "")
        lines.append(f"| `{it['id']}` | `{fname}` | {it['type']} | {human_size(it['size'])} | {title} |")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*Exported by ML OS Ingest Pipeline.*")

    print("\n".join(lines))


# ── WRITE (AI direct-to-vault) ───────────────────────────────

def cmd_write(args):
    """Write content directly to vault, bypassing inbox. Designed for AI agents."""
    project = None
    filename = None
    title = None
    content = None
    use_stdin = False
    dry_run = False

    i = 0
    while i < len(args):
        if args[i] == "--project":
            project = args[i + 1]
            i += 2
        elif args[i] == "--filename":
            filename = args[i + 1]
            i += 2
        elif args[i] == "--title":
            title = args[i + 1]
            i += 2
        elif args[i] == "--content":
            content = args[i + 1]
            i += 2
        elif args[i] == "--stdin":
            use_stdin = True
            i += 1
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            i += 1

    if not project or not filename:
        print("  Usage: python .mlos/ingest.py write --project <name> --filename <name>")
        print("  Provide content via --content \"text\" or --stdin (pipe/heredoc)")
        print("  Optional: --title \"Human-readable title\" --dry-run")
        return

    # Read content from stdin if flagged
    if use_stdin:
        content = sys.stdin.read()
    elif content is None:
        print(f"  {RED}Error: No content provided. Use --content \"text\" or --stdin{R}")
        return

    # Ensure vault project dir exists
    vault_project = VAULT_DIR / project
    if not dry_run:
        vault_project.mkdir(parents=True, exist_ok=True)

    # Handle filename collisions
    index = load_index()
    dest_name = filename
    dest = vault_project / dest_name

    if dest.exists() or index_has_file(index, dest_name, project):
        stem = Path(dest_name).stem
        suffix = Path(dest_name).suffix
        counter = 2
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_dest = vault_project / new_name
            if not new_dest.exists() and not index_has_file(index, new_name, project):
                print(f"  {Y}Renamed: {dest_name} → {new_name} (collision){R}")
                dest_name = new_name
                dest = new_dest
                break
            counter += 1

    # Build index entry
    content_bytes = content.encode("utf-8")
    entry = {
        "id": generate_id(dest_name),
        "filename": dest_name,
        "type": file_type(Path(dest_name)),
        "size": len(content_bytes),
        "title": title or _derive_title(dest_name, content),
        "ingested": datetime.now().strftime("%Y-%m-%d"),
        "project": project,
        "source": "agent",
    }

    if dry_run:
        print(f"\n  {Y}(DRY RUN){R}")
        print(f"  Would write: vault/{project}/{dest_name}")
        print(f"  Size: {human_size(len(content_bytes))}")
        print(f"  Title: {entry['title']}")
        print(f"  ID: {entry['id']}")
        print()
        return

    # Write file
    dest.write_text(content, encoding="utf-8")

    # Update index
    index["items"].append(entry)
    save_index(index)

    # Log event
    log_event("write", project=project, filename=dest_name,
              item_id=entry["id"], type=entry["type"], size=entry["size"])

    print(f"\n  {G}{B}Written to vault/{project}/{dest_name}{R}")
    print(f"  {D}ID: {entry['id']} | Type: {entry['type']} | Size: {human_size(entry['size'])}{R}")
    print(f"  {D}Title: {entry['title']}{R}")
    print()

    # Auto integrity check
    _post_op_check()


def _derive_title(filename, content):
    """Derive a title from content if none provided."""
    # Try first markdown heading
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()[:120]
    # Fallback to cleaned filename
    return Path(filename).stem.replace("_", " ").replace("-", " ")


# ── SYNC (Tier 1 — Mechanical Context Maintenance) ──────────

def cmd_sync(args):
    """Regenerate project-state.md from truth sources (filesystem + index).

    This is Tier 1 mechanical maintenance — no LLM needed. Everything in
    project-state.md can be derived from the current state of the repo.
    """
    dry_run = "--dry-run" in args

    # ── Gather truth from filesystem ──────────────────────────
    index = load_index()
    items = index.get("items", [])

    # Vault projects: directories under vault/
    vault_projects = {}
    if VAULT_DIR.exists():
        for d in sorted(VAULT_DIR.iterdir()):
            if d.is_dir() and d.name not in SKIP_DIRS and d.name != ".gitkeep":
                files = [f for f in d.rglob("*") if f.is_file() and f.name not in SKIP_FILES]
                vault_projects[d.name] = {
                    "files": len(files),
                    "size": sum(f.stat().st_size for f in files),
                }

    # Bench projects
    bench_dir = ROOT / "bench"
    bench_projects = []
    if bench_dir.exists():
        for d in sorted(bench_dir.iterdir()):
            if d.is_dir() and d.name not in SKIP_DIRS:
                bench_projects.append(d.name)

    # Inbox state
    inbox_files = []
    if INBOX_DIR.exists():
        inbox_files = [f for f in INBOX_DIR.rglob("*") if f.is_file() and f.name not in SKIP_FILES]

    # Index stats
    by_project = {}
    by_source = {"agent": 0, "inbox": 0}
    total_size = 0
    for item in items:
        proj = item["project"]
        by_project.setdefault(proj, []).append(item)
        src = item.get("source", "inbox")
        by_source[src] = by_source.get(src, 0) + 1
        total_size += item.get("size", 0)

    # System tools: check what exists in .mlos/
    mlos_tools = []
    if MLOS_DIR.exists():
        for f in sorted(MLOS_DIR.iterdir()):
            if f.is_file() and f.suffix == ".py":
                mlos_tools.append(f.name)

    # Vault browser status
    server_py = ROOT / "server.py"
    index_html = ROOT / "index.html"
    browser_exists = server_py.exists() and index_html.exists()

    # ClaudeTest status (check if sibling repo exists)
    claudetest = ROOT.parent / "ClaudeTest"
    claudetest_exists = claudetest.exists() and (claudetest / "index.html").exists()

    # ── Generate project-state.md ─────────────────────────────
    lines = []
    lines.append("# ML OS Project State")
    lines.append("")
    lines.append(f"> Auto-generated by `ingest.py sync` on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> Source: filesystem scan + index.json (deterministic, no LLM)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## What ML OS Is")
    lines.append("")
    lines.append("A **Meta-Language Operating System** — a layered framework for composing AI agent system prompts and managing the context they operate on. Five layers:")
    lines.append("")
    lines.append("| Layer | OS Analogy | Role |")
    lines.append("|-------|-----------|------|")
    lines.append("| S1 ML OS Core | Kernel/Firmware | Immutable identity, constants, boot sequence |")
    lines.append("| S2 AI Schema | CPU/Runtime | Reasoning protocol, interaction style, output behavior |")
    lines.append("| S3 Scenario | App Layer | Role definition, objectives, evaluation criteria |")
    lines.append("| S4 Sources | Storage/Input | Documents, datasets, transcripts |")
    lines.append("| S5 Outputs | Display/Results | Structured deliverables |")
    lines.append("")
    lines.append("Key concepts:")
    lines.append("- **Bridge Pattern** (from Notion Bridge Architect): Brain <-> Bridge Agent <-> Execution Platform")
    lines.append("- **Master Context Document**: Living, self-updating document tracking workspace state")
    lines.append("- **Context Packs**: Curated sets of files + agent prompts for specific purposes")
    lines.append("- **Template Composition**: Kernel + Schema + Scenario YAML -> full system prompt")
    lines.append("")

    # ── ClaudeTest section ────────────────────────────────────
    lines.append("## What Exists (Two Repos)")
    lines.append("")
    lines.append("### ClaudeTest/ (C:\\Users\\Erinh\\Desktop\\ClaudeTest)")
    lines.append("")
    if claudetest_exists:
        lines.append("The **prototyping sandbox**. Contains:")
        lines.append("")
        lines.append("- `index.html` + `src/` -- Interactive ML OS web demo (boot sequence, dashboard, agent instantiation)")
        lines.append("- `server.py` -- Python HTTP dev server (port 3000)")
        lines.append("- `mlos.py` -- **Template Composer CLI** (list, compose, boot, create)")
        lines.append("- `cowork.py` -- **Agent Orchestration CLI** (init, status, dispatch, assign, report, sync, history, memory)")
        lines.append("- `.mlos/` -- kernel.yaml, schema.yaml, scenarios/, registry.yaml, context.md")
    else:
        lines.append("*(Not found on this machine)*")
    lines.append("")

    # ── Home_Lab_2026 section ─────────────────────────────────
    lines.append("### Home_Lab_2026/ (C:\\Users\\Erinh\\Desktop\\Home_Lab_2026)")
    lines.append("")
    lines.append("The **vault system** (Claude-Cowork-Vault). Contains:")
    lines.append("")

    # Vault projects with actual counts
    for proj, stats in vault_projects.items():
        indexed_count = len(by_project.get(proj, []))
        lines.append(f"- `vault/{proj}/` -- {stats['files']} file(s) on disk, {indexed_count} indexed ({human_size(stats['size'])})")

    if not vault_projects:
        lines.append("- `vault/` -- No project directories yet")

    # Bench
    if bench_projects:
        for proj in bench_projects:
            lines.append(f"- `bench/{proj}/` -- Work products directory")
    else:
        lines.append("- `bench/` -- No bench projects yet")

    # Inbox
    lines.append(f"- `io/inbox/` -- {'Empty' if not inbox_files else f'{len(inbox_files)} file(s) waiting'}")
    lines.append("")

    # System tools
    lines.append("**System tools** (`.mlos/`):")
    for tool in mlos_tools:
        if tool == "ingest.py":
            lines.append(f"- `ingest.py` -- Vault pipeline (scan, add, write, view, check, export, sync)")
        elif tool == "moc.py":
            lines.append(f"- `moc.py` -- Auto MOC generator")
        elif tool == "fix_encoding.py":
            lines.append(f"- `fix_encoding.py` -- UTF-8 mojibake fixer")
        else:
            lines.append(f"- `{tool}`")
    lines.append("")

    # Vault browser
    if browser_exists:
        lines.append("**Vault browser**: `server.py` (port 3001) + `index.html` -- local web UI for browsing vault contents")
    else:
        lines.append("**Vault browser**: Not yet built")
    lines.append("")

    lines.append("**Repo**: https://github.com/mrmeman555/Claude-Cowork-Vault.git")
    lines.append("")

    # ── Index summary ─────────────────────────────────────────
    lines.append("## Current Index State")
    lines.append("")
    lines.append(f"- **Total items**: {len(items)}")
    lines.append(f"- **Total size**: {human_size(total_size)}")
    lines.append(f"- **Agent-created**: {by_source.get('agent', 0)}")
    lines.append(f"- **Inbox-ingested**: {by_source.get('inbox', 0)}")
    lines.append(f"- **Projects**: {', '.join(sorted(by_project.keys())) if by_project else 'none'}")
    if items:
        lines.append(f"- **Last updated**: {index.get('last_updated', 'unknown')}")
    lines.append("")

    if by_project:
        lines.append("### By Project")
        lines.append("")
        for proj, proj_items in sorted(by_project.items()):
            proj_size = sum(it.get("size", 0) for it in proj_items)
            lines.append(f"**{proj}/** ({len(proj_items)} items, {human_size(proj_size)}):")
            for it in sorted(proj_items, key=lambda x: x["filename"]):
                lines.append(f"- `{it['filename']}` -- {it.get('title', it['filename'])} ({it['type']}, {human_size(it.get('size', 0))})")
            lines.append("")

    # ── Status summary ────────────────────────────────────────
    lines.append("## Current Status")
    lines.append("")
    lines.append(f"- Vault structure: **{'populated' if any(s['files'] > 0 for s in vault_projects.values()) else 'ready'}** ({len(vault_projects)} project dir(s))")
    lines.append(f"- Ingest pipeline: **functional** (scan, add, write, view, check, export, sync)")
    lines.append(f"- Index: **{len(items)} item(s)** indexed")
    lines.append(f"- Storage: **git** (git is the persistence layer)")
    lines.append(f"- Vault browser: **{'running' if browser_exists else 'not started'}** {'(server.py port 3001)' if browser_exists else ''}")
    lines.append(f"- Inbox: **{'empty' if not inbox_files else f'{len(inbox_files)} file(s) pending'}**")

    # Task summary across projects
    total_open = 0
    total_in_progress = 0
    total_done = 0
    for proj in vault_projects:
        tpath = VAULT_DIR / proj / "tasks.json"
        if tpath.exists():
            try:
                with open(tpath, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                for t in tdata.get("tasks", []):
                    if t.get("status") == "open": total_open += 1
                    elif t.get("status") == "in_progress": total_in_progress += 1
                    elif t.get("status") == "done": total_done += 1
            except (json.JSONDecodeError, IOError):
                pass
    if total_open or total_in_progress or total_done:
        lines.append(f"- Tasks: **{total_open} open**, **{total_in_progress} in progress**, **{total_done} done**")

    lines.append("")

    # ── Roles ─────────────────────────────────────────────────
    lines.append("## Who Works Here")
    lines.append("")
    lines.append("- **Cloud agent (claude.ai / Cowork):** Writes docs, plans changes, designs systems")
    lines.append("- **Local agent (Claude Code):** Pulls repo, executes, builds tools, processes files")
    lines.append("- **Operator (Mimir):** Relays between agents, final authority")
    lines.append("")
    lines.append("## Ground Rules")
    lines.append("")
    lines.append("- Do NOT modify vault files without asking the operator first")
    lines.append("- Do NOT run scripts without showing what they'll do")
    lines.append("- Read first, understand second, suggest third, act only when operator says go")

    content = "\n".join(lines) + "\n"

    # ── Output ────────────────────────────────────────────────
    dest = VAULT_DIR / "mlos-dev" / "project-state.md"

    if dry_run:
        print(f"\n  {Y}(DRY RUN) Would regenerate:{R}")
        print(f"  {dest.relative_to(ROOT)}")
        print(f"  Size: {human_size(len(content.encode('utf-8')))}")
        print(f"\n  {D}Preview:{R}")
        for line in content.split("\n")[:20]:
            print(f"    {line}")
        print(f"    ... ({len(content.split(chr(10)))} total lines)")
        print()
        return

    # Ensure directory exists
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")

    # Update index entry size
    new_size = len(content.encode("utf-8"))
    for item in index["items"]:
        if item["filename"] == "project-state.md" and item["project"] == "mlos-dev":
            item["size"] = new_size
            break
    save_index(index)

    # Log event
    log_event("sync", target="project-state.md", size=new_size,
              index_items=len(items), vault_projects=len(vault_projects))

    print(f"\n  {G}{B}Synced: vault/mlos-dev/project-state.md{R}")
    print(f"  {D}Derived from: filesystem scan + index.json{R}")
    print(f"  {D}Size: {human_size(new_size)} | {len(content.split(chr(10)))} lines{R}")
    print()


# ── LOG (View Event History) ─────────────────────────────────

def cmd_log(args):
    """View the event log. Shows recent vault operations."""
    # Parse args
    limit = 20
    action_filter = None
    i = 0
    while i < len(args):
        if args[i] == "--limit" or args[i] == "-n":
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "--action":
            action_filter = args[i + 1]
            i += 2
        else:
            i += 1

    if not EVENT_LOG_PATH.exists():
        print(f"\n  {D}No events logged yet. Events are recorded when you add, write, sync, or check.{R}\n")
        return

    # Read all events
    events = []
    with open(EVENT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if action_filter:
        events = [e for e in events if e.get("action") == action_filter]

    if not events:
        print(f"\n  {D}No matching events.{R}\n")
        return

    # Show most recent first, limited
    events = events[-limit:]
    events.reverse()

    print(f"\n  {G}{B}Event Log — {len(events)} event(s){R}")
    if action_filter:
        print(f"  {D}Filter: action={action_filter}{R}")
    print()

    for ev in events:
        ts = ev.get("timestamp", "?")
        action = ev.get("action", "?")
        # Color by action type
        color = {
            "add": G, "write": C, "sync": M, "check": Y,
            "task_add": G, "task_update": C, "task_done": G,
        }.get(action, D)

        # Format details
        details = []
        if "project" in ev:
            details.append(ev["project"])
        if "filename" in ev:
            details.append(ev["filename"])
        if "target" in ev:
            details.append(ev["target"])
        if "title" in ev:
            details.append(ev["title"][:50])
        if "result" in ev:
            details.append(f"result={ev['result']}")
        if "changes" in ev:
            details.append(ev["changes"])
        if "size" in ev:
            details.append(human_size(ev["size"]))

        detail_str = " | ".join(details) if details else ""
        print(f"  {D}{ts}{R}  {color}{B}{action:<6}{R}  {detail_str}")

    print()


# ── Task Commands ─────────────────────────────────────────────

def cmd_task_add(args):
    project = None
    title = None
    priority = "medium"
    task_type = "task"
    tags = []
    notes = ""

    i = 0
    while i < len(args):
        if args[i] == "--project" and i + 1 < len(args):
            project = args[i + 1]; i += 2
        elif args[i] == "--title" and i + 1 < len(args):
            title = args[i + 1]; i += 2
        elif args[i] == "--priority" and i + 1 < len(args):
            priority = args[i + 1]; i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            task_type = args[i + 1]; i += 2
        elif args[i] == "--tags" and i + 1 < len(args):
            tags = [t.strip() for t in args[i + 1].split(",")]; i += 2
        elif args[i] == "--notes" and i + 1 < len(args):
            notes = args[i + 1]; i += 2
        else:
            i += 1

    if not project or not title:
        print(f"  {RED}Usage: task add --project <name> --title \"...\"{R}")
        print(f"  {D}Optional: --priority high|medium|low --type task|idea --tags a,b --notes \"...\"{R}")
        return

    # Validate project dir exists
    project_dir = VAULT_DIR / project
    if not project_dir.exists():
        print(f"  {RED}Project directory not found: vault/{project}/{R}")
        return

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    task = {
        "id": generate_task_id(title),
        "title": title,
        "status": "open",
        "priority": priority,
        "type": task_type,
        "created": now,
        "updated": now,
        "tags": tags,
        "notes": notes,
    }

    data = load_tasks(project)
    data["tasks"].append(task)
    save_tasks(project, data)

    log_event("task_add", project=project, task_id=task["id"], title=title, type=task_type)

    print(f"\n  {G}{B}Task created in {project}/{R}")
    print(f"  {D}ID: {task['id']} | Priority: {priority} | Type: {task_type}{R}")
    print(f"  {C}{title}{R}\n")


def cmd_task_list(args):
    project_filter = None
    status_filter = None
    type_filter = None
    tag_filter = None

    i = 0
    while i < len(args):
        if args[i] == "--project" and i + 1 < len(args):
            project_filter = args[i + 1]; i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            status_filter = args[i + 1]; i += 2
        elif args[i] == "--type" and i + 1 < len(args):
            type_filter = args[i + 1]; i += 2
        elif args[i] == "--tag" and i + 1 < len(args):
            tag_filter = args[i + 1]; i += 2
        else:
            i += 1

    # Collect tasks from project(s)
    all_tasks = []
    if project_filter:
        projects = [project_filter]
    else:
        projects = [d.name for d in VAULT_DIR.iterdir()
                    if d.is_dir() and not d.name.startswith(".")]

    for proj in sorted(projects):
        data = load_tasks(proj)
        for t in data.get("tasks", []):
            all_tasks.append((proj, t))

    # Apply filters
    if status_filter:
        all_tasks = [(p, t) for p, t in all_tasks if t["status"] == status_filter]
    if type_filter:
        all_tasks = [(p, t) for p, t in all_tasks if t["type"] == type_filter]
    if tag_filter:
        all_tasks = [(p, t) for p, t in all_tasks if tag_filter in t.get("tags", [])]

    if not all_tasks:
        print(f"\n  {D}No tasks found.{R}\n")
        return

    # Group by project
    by_project = {}
    for proj, task in all_tasks:
        by_project.setdefault(proj, []).append(task)

    STATUS_COLOR = {"open": Y, "in_progress": C, "done": G, "dropped": D}

    print(f"\n  {G}{B}Tasks — {len(all_tasks)} item(s){R}")
    filters = []
    if status_filter: filters.append(f"status={status_filter}")
    if type_filter: filters.append(f"type={type_filter}")
    if tag_filter: filters.append(f"tag={tag_filter}")
    if filters:
        print(f"  {D}Filters: {', '.join(filters)}{R}")
    print()

    for proj, tasks in sorted(by_project.items()):
        print(f"  {C}{B}{proj}/{R}")
        print(f"  {'ID':<10} {'Status':<14} {'Pri':<8} {'Type':<6} Title")
        print(f"  {'-'*10} {'-'*14} {'-'*8} {'-'*6} {'-'*40}")
        for t in tasks:
            sc = STATUS_COLOR.get(t["status"], D)
            print(f"  {t['id']:<10} {sc}{t['status']:<14}{R} {t['priority']:<8} {t['type']:<6} {t['title'][:50]}")
        print()


def cmd_task_update(args):
    task_id = None
    project = None
    new_status = None
    new_priority = None
    new_title = None
    new_notes = None
    new_tags = None

    i = 0
    while i < len(args):
        if args[i] == "--project" and i + 1 < len(args):
            project = args[i + 1]; i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            new_status = args[i + 1]; i += 2
        elif args[i] == "--priority" and i + 1 < len(args):
            new_priority = args[i + 1]; i += 2
        elif args[i] == "--title" and i + 1 < len(args):
            new_title = args[i + 1]; i += 2
        elif args[i] == "--notes" and i + 1 < len(args):
            new_notes = args[i + 1]; i += 2
        elif args[i] == "--tags" and i + 1 < len(args):
            new_tags = [t.strip() for t in args[i + 1].split(",")]; i += 2
        elif not args[i].startswith("--"):
            task_id = args[i]; i += 1
        else:
            i += 1

    if not task_id:
        print(f"  {RED}Usage: task update <id> [--status ...] [--priority ...] [--title \"...\"] [--notes \"...\"] [--tags a,b]{R}")
        return

    found_project, found_task, data = _find_task(task_id, project)
    if not found_task:
        print(f"  {RED}Task not found: {task_id}{R}")
        return

    changes = []
    if new_status:
        found_task["status"] = new_status; changes.append(f"status={new_status}")
    if new_priority:
        found_task["priority"] = new_priority; changes.append(f"priority={new_priority}")
    if new_title:
        found_task["title"] = new_title; changes.append("title updated")
    if new_notes:
        found_task["notes"] = new_notes; changes.append("notes updated")
    if new_tags is not None:
        found_task["tags"] = new_tags; changes.append("tags updated")

    if not changes:
        print(f"  {D}No changes specified.{R}")
        return

    found_task["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_tasks(found_project, data)

    log_event("task_update", project=found_project, task_id=task_id, changes=", ".join(changes))

    print(f"\n  {G}Updated {task_id}: {', '.join(changes)}{R}\n")


def cmd_task_done(args):
    task_id = None
    project = None

    i = 0
    while i < len(args):
        if args[i] == "--project" and i + 1 < len(args):
            project = args[i + 1]; i += 2
        elif not args[i].startswith("--"):
            task_id = args[i]; i += 1
        else:
            i += 1

    if not task_id:
        print(f"  {RED}Usage: task done <id> [--project <name>]{R}")
        return

    found_project, found_task, data = _find_task(task_id, project)
    if not found_task:
        print(f"  {RED}Task not found: {task_id}{R}")
        return

    found_task["status"] = "done"
    found_task["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    save_tasks(found_project, data)

    log_event("task_done", project=found_project, task_id=task_id, title=found_task["title"])

    print(f"\n  {G}{B}Done: {found_task['title']}{R}")
    print(f"  {D}ID: {task_id} | Project: {found_project}{R}\n")


TASK_SUBCOMMANDS = {
    "add": cmd_task_add,
    "list": cmd_task_list,
    "update": cmd_task_update,
    "done": cmd_task_done,
}

def cmd_task(args):
    """Task tracking: add, list, update, done."""
    if not args:
        print(f"\n  {B}Task Tracking{R}")
        print(f"  {D}Usage: python .mlos/ingest.py task <add|list|update|done> [options]{R}")
        print(f"\n  {C}add{R}    --project <name> --title \"...\" [--priority high|medium|low] [--type task|idea] [--tags a,b] [--notes \"...\"]")
        print(f"  {C}list{R}   [--project <name>] [--status open|in_progress|done|dropped] [--type task|idea] [--tag <tag>]")
        print(f"  {C}update{R} <id> [--status ...] [--priority ...] [--title \"...\"] [--notes \"...\"] [--tags a,b]")
        print(f"  {C}done{R}   <id> [--project <name>]")
        print()
        return

    sub = args[0]
    sub_args = args[1:]
    if sub in TASK_SUBCOMMANDS:
        TASK_SUBCOMMANDS[sub](sub_args)
    else:
        print(f"  {RED}Unknown task command: {sub}{R}")
        print(f"  {D}Available: add, list, update, done{R}")


# ── CLI Router ────────────────────────────────────────────────

COMMANDS = {
    "scan": cmd_scan,
    "add": cmd_add,
    "write": cmd_write,
    "view": cmd_view,
    "check": cmd_check,
    "export": cmd_export,
    "sync": cmd_sync,
    "log": cmd_log,
    "task": cmd_task,
}

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd in COMMANDS:
        COMMANDS[cmd](args)
    else:
        print(f"  {RED}Unknown command: {cmd}{R}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
