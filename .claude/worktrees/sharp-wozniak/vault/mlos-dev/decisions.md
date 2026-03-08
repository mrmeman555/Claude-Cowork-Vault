# Architectural Decisions Log

> Key design decisions made during ML OS development, with rationale.
> Newest first.

---

## D-007: Context Packs as Vault Projects (2026-03-05)

**Decision:** Store ML OS development context as a vault project (`mlos-dev`), making it loadable by any new session.

**Why:** Every new Claude session starts cold. Re-reading all files wastes context window. A curated context pack gives instant orientation — state, decisions, history — without re-exploring.

**Alternative rejected:** Relying solely on CLAUDE.md + auto-memory. These are too shallow — they capture what exists but not why, and don't preserve conversation-level reasoning.

---

## D-006: Git as Primary Storage (2026-03-05)

**Decision:** Use git as the vault storage layer. Home web server comes later as the frontend host.

**Why:** Git is already working (repo exists on GitHub), gives version history for free, enables multi-device access via pull. For small, curated vaults, repo size won't be an issue. Git LFS available if needed.

**Architecture:**
```
Storage:  git repo (vault files + index.json)
System:   .mlos/ (ingest, moc, agents, prompts)
AI:       Claude (reads, writes, commits)
Visual:   Frontend app (future, served from home server)
```

---

## D-005: AI Direct-to-Vault Write Path (2026-03-05)

**Decision:** AI-generated content goes directly to vault via `write` command, not through inbox.

**Why:** Inbox is for human-dropped files that need classification. Claude already knows what it's creating and where it goes. The `source: agent` field in the index distinguishes AI-created from human-ingested content.

---

## D-004: 8-Char Hex Hash IDs (2026-03-05)

**Decision:** Use 8-character hex hash of `filename:timestamp` as item IDs.

**Why:** Collision-resistant, no ordering dependency, works across projects. Opaque but short enough for display and references. Sequential IDs (sp-001) break if items are added out of order across sessions.

---

## D-003: Inbox-Only Ingest Source (2026-03-05)

**Decision:** The `add` command only ingests from `io/inbox/`. Files must be placed there first.

**Why:** Single entry point prevents accidental ingestion of system files or work-in-progress. Clear boundary: if it's in inbox, it's ready to be processed. The `write` command exists for the AI path, which doesn't need this guard.

---

## D-002: Flatten vs Preserve — Ask Each Time (2026-03-05)

**Decision:** When ingesting folders with subfolders, prompt the user to choose flatten or preserve. CLI flags (`--flatten`/`--preserve`) available to skip the prompt.

**Why:** No single default works for all cases. A flat GitHub repo clone should be flattened. A structured course folder should be preserved. Interactive prompt shows the structure before asking, so the decision is informed.

---

## D-001: Minimal 6-Field Index Schema (2026-03-05)

**Decision:** Start with only auto-derivable fields: id, filename, type, size, title, ingested, project. No paths stored.

**Why:** Every field can be populated by a script with zero human judgment. Richer metadata (tags, objectives, blooms_level) gets added later in batches when a specific task demands it. Paths are derived from `vault/{project}/{filename}` — no stale paths, one find-replace to rename a project.

**Tradeoff:** Filenames must be unique within a project. Collision handling auto-renames at ingest time.

---

## D-000: Vault/Bench/Inbox Architecture (2026-03-04)

**Decision:** Three-zone structure: vault (immutable stored materials), bench (work products referencing vault items), io/inbox (raw drop zone).

**Why:** Clear separation of concerns. Vault files don't change once placed. Bench files are analysis artifacts that reference vault items. Inbox is the staging area. Projects mirror across vault and bench by name.
