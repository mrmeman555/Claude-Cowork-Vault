#!/usr/bin/env python3
"""
ML OS — Auto MOC (Map of Content) Generator

Scans a directory and generates/updates a MOC markdown file cataloging
every file with type, size, and heading extraction.

Usage:
  python .mlos/moc.py <directory>                  Print MOC to stdout
  python .mlos/moc.py <directory> -o               Write MOC.md inside the directory
  python .mlos/moc.py <directory> -o path/to/out.md Write MOC to specific path
  python .mlos/moc.py <directory> --depth 2        Limit directory depth (default: unlimited)
  python .mlos/moc.py <directory> --flat            No subdirectory grouping, just a flat list

Examples:
  python .mlos/moc.py Docs/net+Analysis
  python .mlos/moc.py io/inbox -o --depth 1
  python .mlos/moc.py Sec+Analysis -o Sec+Analysis/MOC.md
"""

import sys
import os
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Files to skip in MOC generation
SKIP_FILES = {".DS_Store", "Thumbs.db", ".gitignore", ".cursorindexingignore"}
SKIP_DIRS = {".git", ".mlos", "__pycache__", ".specstory", "node_modules", ".venv"}
MOC_FILENAME = "MOC.md"

# ── File Type Detection ───────────────────────────────────────

FILE_TYPES = {
    ".md": "markdown",
    ".txt": "text",
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "doc",
    ".csv": "csv",
    ".html": "html",
    ".css": "css",
    ".sh": "shell",
    ".bat": "batch",
    ".ps1": "powershell",
    ".ipynb": "notebook",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".svg": "image",
}


def file_type(path):
    return FILE_TYPES.get(path.suffix.lower(), path.suffix.lower().lstrip(".") or "file")


def human_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ── Heading Extraction ────────────────────────────────────────

def extract_heading(path):
    """Extract the first meaningful heading or description from a file."""
    try:
        if path.suffix.lower() == ".md":
            return _heading_from_markdown(path)
        elif path.suffix.lower() == ".py":
            return _heading_from_python(path)
        elif path.suffix.lower() in (".yaml", ".yml"):
            return _heading_from_yaml(path)
        elif path.suffix.lower() == ".json":
            return _heading_from_json(path)
        elif path.suffix.lower() == ".txt":
            return _heading_from_text(path)
        elif path.suffix.lower() == ".docx":
            return _heading_from_docx(path)
    except Exception:
        pass
    return None


def _heading_from_markdown(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()
            if line and not line.startswith(">") and not line.startswith("---"):
                return line[:80]
    return None


def _heading_from_python(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(500)
    # Look for docstring
    for marker in ['"""', "'''"]:
        if marker in content:
            start = content.index(marker) + 3
            end = content.find(marker, start)
            if end > start:
                doc = content[start:end].strip().split("\n")[0]
                return doc[:80]
    # Look for first comment
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("#") and not line.startswith("#!"):
            return line.lstrip("#").strip()[:80]
    return None


def _heading_from_yaml(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()[:80]
            if line and ":" in line:
                return line[:80]
    return None


def _heading_from_json(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(200)
    if '"name"' in content:
        import json
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if isinstance(data, dict) and "name" in data:
                return str(data["name"])[:80]
        except Exception:
            pass
    return None


def _heading_from_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                return line[:80]
    return None


def _heading_from_docx(path):
    """Try to extract title from docx without python-docx (just filename heuristic)."""
    # Parse lab-style filenames: SecPlusLM_8e_Lab04-2.docx -> "Lab 04-2"
    name = path.stem
    if "Lab" in name:
        parts = name.split("Lab")
        if len(parts) > 1:
            return f"Lab {parts[-1]}"
    return None


# ── Directory Scanner ─────────────────────────────────────────

def scan_directory(root, max_depth=None):
    """Scan directory and return structured file info grouped by subdirectory."""
    root = Path(root).resolve()
    files_by_dir = defaultdict(list)

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out skipped directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        current = Path(dirpath)
        depth = len(current.relative_to(root).parts)

        if max_depth is not None and depth > max_depth:
            dirnames.clear()
            continue

        for fname in sorted(filenames):
            if fname in SKIP_FILES or fname == MOC_FILENAME:
                continue

            fpath = current / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                size = 0

            rel_dir = current.relative_to(root)
            rel_file = fpath.relative_to(root)

            files_by_dir[str(rel_dir)].append({
                "name": fname,
                "path": str(rel_file),
                "type": file_type(fpath),
                "size": size,
                "size_human": human_size(size),
                "heading": extract_heading(fpath),
            })

    return files_by_dir


# ── MOC Rendering ─────────────────────────────────────────────

def render_moc(root, files_by_dir, flat=False):
    root = Path(root)
    root_name = root.name

    # Stats
    total_files = sum(len(files) for files in files_by_dir.values())
    total_size = sum(f["size"] for files in files_by_dir.values() for f in files)
    type_counts = defaultdict(int)
    for files in files_by_dir.values():
        for f in files:
            type_counts[f["type"]] += 1

    lines = []
    p = lines.append

    p(f"# MOC — {root_name}")
    p(f"")
    p(f"> Auto-generated by ML OS MOC Generator")
    p(f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    p(f"> Scanned: `{root_name}/`")
    p(f"")
    p(f"---")
    p(f"")

    # Summary
    p(f"## Summary")
    p(f"")
    p(f"- **Total files:** {total_files}")
    p(f"- **Total size:** {human_size(total_size)}")
    p(f"- **Directories:** {len(files_by_dir)}")
    p(f"")

    # Type breakdown
    if type_counts:
        p(f"| Type | Count |")
        p(f"|------|-------|")
        for ftype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            p(f"| {ftype} | {count} |")
        p(f"")

    p(f"---")
    p(f"")

    if flat:
        # Flat list
        p(f"## Files")
        p(f"")
        p(f"| File | Type | Size | Description |")
        p(f"|------|------|------|-------------|")
        for dir_key in sorted(files_by_dir.keys()):
            for f in files_by_dir[dir_key]:
                desc = f["heading"] or ""
                path = f["path"].replace("\\", "/")
                p(f"| `{path}` | {f['type']} | {f['size_human']} | {desc} |")
        p(f"")
    else:
        # Grouped by directory
        p(f"## Contents")
        p(f"")

        for dir_key in sorted(files_by_dir.keys()):
            files = files_by_dir[dir_key]
            if dir_key == ".":
                p(f"### Root")
            else:
                p(f"### {dir_key.replace(chr(92), '/')}")
            p(f"")
            p(f"| File | Type | Size | Description |")
            p(f"|------|------|------|-------------|")
            for f in files:
                desc = f["heading"] or ""
                p(f"| `{f['name']}` | {f['type']} | {f['size_human']} | {desc} |")
            p(f"")

    p(f"---")
    p(f"*Generated by ML OS MOC Generator. Re-run to update.*")

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    target = sys.argv[1]
    args = sys.argv[2:]

    # Parse flags
    output = None
    depth = None
    flat = False

    i = 0
    while i < len(args):
        if args[i] == "-o":
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                output = args[i + 1]
                i += 2
            else:
                output = True  # Write to default location
                i += 1
        elif args[i] == "--depth":
            depth = int(args[i + 1])
            i += 2
        elif args[i] == "--flat":
            flat = True
            i += 1
        else:
            i += 1

    root = Path(target).resolve()
    if not root.exists():
        print(f"  Error: Directory not found: {root}")
        sys.exit(1)

    files_by_dir = scan_directory(root, max_depth=depth)
    moc = render_moc(root, files_by_dir, flat=flat)

    if output:
        if output is True:
            out_path = root / MOC_FILENAME
        else:
            out_path = Path(output)
        out_path.write_text(moc, encoding="utf-8")
        total = sum(len(f) for f in files_by_dir.values())
        print(f"  MOC written: {out_path} ({total} files cataloged)")
    else:
        print(moc)


if __name__ == "__main__":
    main()
