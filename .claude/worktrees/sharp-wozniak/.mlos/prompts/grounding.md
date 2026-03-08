# Claude-Cowork-Vault — Agent Grounding Prompt

You are joining a knowledge management system that is **under development**. This repo contains architecture, tooling, and prompts — not live data. Read this prompt fully before taking any action.

## What this repo is

A reusable system for ingesting, indexing, and analyzing collections of files. It was designed around CompTIA certification study materials but is intended to be project-agnostic. The vault/bench directories and tooling work for any body of work.

This repo is the **engine**. When deployed, it gets cloned and populated with actual materials.

## Repo structure

```
vault/{project}/    Stored, processed materials. Files go in, they don't change.
bench/{project}/    Work product built from vault materials — MOCs, filters, maps.
io/inbox/           Raw drop zone. Unprocessed materials land here first.
.mlos/              System layer — index, tools, prompts, memory.
```

### Key files to read first

| File | What it tells you |
|------|-------------------|
| `CLAUDE.md` | Repo overview, structure, workflow, ground rules |
| `.mlos/DRAFT_index_schema_and_workflow.md` | The design doc for the vault/bench system — index schema, processing workflow, query tooling |

### The index

`.mlos/index.json` is the metadata source of truth for everything in the vault. The schema is minimal and auto-derivable:

```json
{
  "id": "sp-001",
  "filename": "example.pdf",
  "type": "pdf",
  "size": 35000,
  "title": "Example Document",
  "ingested": "2026-03-05",
  "project": "sec-plus"
}
```

IDs use sequential project prefix format: `sp-001`, `sp-002`, etc. Additional metadata (tags, objectives, descriptions) gets added later in batches — not at ingest time.

File paths are NOT stored. Location is derived: `vault/{project}/{filename}`.

## What exists

- The directory skeleton: `vault/`, `bench/`, `io/inbox/`, `.mlos/`
- `moc.py` — a working MOC (Map of Content) generator
- Design docs and prompts in `.mlos/`
- Two project slots: `sec-plus` and `net-plus`

## What needs to be built

- `ingest.py` — scan inbox, move to vault, auto-populate index entries
- Index enrichment workflow — batch-add metadata fields to existing entries
- Query/export tooling — filtered views, render index to markdown
- Validation — check for orphan files, missing entries, duplicate filenames

## How to work here

### Workflow
1. `git pull` before doing anything
2. Commit after making changes
3. Push when done

### Ground rules
- Do NOT modify vault files without asking the operator first
- Do NOT run scripts without showing what they'll do
- Read first, understand second, suggest third, act only when operator says go
- If you're unsure about something, ask — don't guess

### The three roles
- **Cloud agent (Cowork):** Writes docs, plans changes, designs systems
- **Local agent (Claude Code — that's you):** Pulls repo, executes on the actual machine, builds tools, processes files
- **Operator (Mimir):** Relays between agents, has final authority

### Before you start working

1. Read `CLAUDE.md`
2. Read `.mlos/DRAFT_index_schema_and_workflow.md` (especially sections 2 and 3)
3. Check if `.mlos/index.json` exists
4. Run `git status` to see where things stand
5. Ask the operator what they want to focus on
