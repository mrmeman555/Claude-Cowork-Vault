#!/usr/bin/env python3
"""
merge-driver.py — Custom git merge driver for ML OS vault files.

Handles two file types:
  - .mlos/events.jsonl   — append-only event log, merge by concatenating + dedup by timestamp
  - vault/**/tasks.json  — merge by task ID, newer updated timestamp wins on conflict

Usage (called by git, not directly):
  python3 .mlos/merge-driver.py %O %A %B <filetype>

Arguments:
  %O = base (common ancestor)
  %A = ours (current branch) — we write result here
  %B = theirs (incoming branch)
  filetype = "events" or "tasks"

Exit codes:
  0 = merge successful, %A updated with result
  1 = merge failed (git will fall back to conflict markers)
"""

import json
import sys
import os
from pathlib import Path


def merge_events(base_path, ours_path, theirs_path):
    """Merge append-only .jsonl event logs by combining all entries, dedup by timestamp+action."""

    def read_jsonl(path):
        entries = []
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except FileNotFoundError:
            pass
        return entries

    base = read_jsonl(base_path)
    ours = read_jsonl(ours_path)
    theirs = read_jsonl(theirs_path)

    # Combine all entries
    all_entries = ours + theirs

    # Deduplicate: use (timestamp, action, target/project) as key
    seen = set()
    unique = []
    for entry in all_entries:
        key = (
            entry.get("timestamp", ""),
            entry.get("action", ""),
            entry.get("target", entry.get("project", entry.get("filename", "")))
        )
        if key not in seen:
            seen.add(key)
            unique.append(entry)

    # Sort chronologically
    unique.sort(key=lambda e: e.get("timestamp", ""))

    # Write result to ours_path (git reads %A as the result)
    with open(ours_path, "w") as f:
        for entry in unique:
            f.write(json.dumps(entry) + "\n")

    return True


def merge_tasks(base_path, ours_path, theirs_path):
    """Merge tasks.json by task ID — newer updated timestamp wins on conflict."""

    def read_tasks(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    base = read_tasks(base_path)
    ours = read_tasks(ours_path)
    theirs = read_tasks(theirs_path)

    if ours is None or theirs is None:
        return False

    # Index tasks by ID
    ours_by_id = {t["id"]: t for t in ours.get("tasks", [])}
    theirs_by_id = {t["id"]: t for t in theirs.get("tasks", [])}

    # Merge: for each task ID, take the version with the newer 'updated' timestamp
    all_ids = set(ours_by_id.keys()) | set(theirs_by_id.keys())
    merged_tasks = []

    for task_id in all_ids:
        ours_task = ours_by_id.get(task_id)
        theirs_task = theirs_by_id.get(task_id)

        if ours_task and theirs_task:
            # Both have it — take newer
            ours_updated = ours_task.get("updated", ours_task.get("created", ""))
            theirs_updated = theirs_task.get("updated", theirs_task.get("created", ""))
            merged_tasks.append(ours_task if ours_updated >= theirs_updated else theirs_task)
        else:
            # Only one side has it
            merged_tasks.append(ours_task or theirs_task)

    # Sort by created timestamp for stable output
    merged_tasks.sort(key=lambda t: t.get("created", ""))

    # Build result using ours as base for metadata
    result = dict(ours)
    result["tasks"] = merged_tasks
    result["last_updated"] = max(
        ours.get("last_updated", ""),
        theirs.get("last_updated", "")
    )

    with open(ours_path, "w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    return True


def main():
    if len(sys.argv) < 4:
        print("Usage: merge-driver.py <base> <ours> <theirs> [filetype]", file=sys.stderr)
        sys.exit(1)

    base_path = sys.argv[1]
    ours_path = sys.argv[2]
    theirs_path = sys.argv[3]

    # Detect filetype from the filename if not passed explicitly
    filetype = sys.argv[4] if len(sys.argv) > 4 else None
    if not filetype:
        if ours_path.endswith(".jsonl"):
            filetype = "events"
        elif "tasks.json" in ours_path:
            filetype = "tasks"
        else:
            # Unknown file — let git handle it
            sys.exit(1)

    if filetype == "events":
        success = merge_events(base_path, ours_path, theirs_path)
    elif filetype == "tasks":
        success = merge_tasks(base_path, ours_path, theirs_path)
    else:
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
