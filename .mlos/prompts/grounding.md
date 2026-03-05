# Claude-Cowork-Vault — Agent Grounding Prompt

You are joining an active knowledge management project. Read this prompt fully before taking any action.

## What this repo is

A personal knowledge vault for organizing study materials and building analysis tools on top of them. The operator is studying for CompTIA certifications (Security+ is the active project, Net+ is completed). Materials include textbooks, lab manuals, exam objectives, community study guides, and deep research outputs.

## Repo structure

```
vault/{project}/    Stored, processed materials. Files go in, they don't change.
bench/{project}/    Work product built from vault materials — MOCs, filters, maps.
io/inbox/           Raw drop zone. Unprocessed materials land here first.
.mlos/              System layer — index, tools, prompts, memory.
Docs/               Legacy Net+ analysis (not yet migrated to vault/bench).
Sec+Analysis/       Legacy Sec+ analysis (not yet migrated to bench/).
```

### Key files to read first

| File | What it tells you |
|------|-------------------|
| `CLAUDE.md` | Repo overview, structure, workflow, ground rules |
| `.mlos/DRAFT_index_schema_and_workflow.md` | The design doc for the vault/bench system (approved direction, not yet fully built) |
| `.mlos/prompts/explore-with-me.md` | The exploration prompt — useful context on the full project history |
| `Sec+Analysis/NetPlus_Recap.md` | Complete walkthrough of the Net+ methodology and what ports to Sec+ |

### The index

`.mlos/index.json` is the metadata source of truth for everything in the vault. If it doesn't exist yet, it needs to be created. The schema is minimal and auto-derivable:

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

IDs use sequential project prefix format: `sp-001`, `sp-002`, etc. for sec-plus. Additional metadata (tags, objectives, descriptions) gets added later in batches — not at ingest time.

File paths are NOT stored in the index. A file's location is derived: `vault/{project}/{filename}`.

## Current state

**Active project:** `sec-plus` (CompTIA Security+ SY0-701)

**What exists:**
- `io/inbox/` has unprocessed Sec+ materials: Cengage labs (.docx), Messer/Dion PDFs, Packt training guide, ryanliupie community notes, deep research outputs, exam objectives PDFs
- `Sec+Analysis/` has two early analysis files (NetPlus_Recap.md, LabAnalysis.md) — these should eventually move to `bench/sec-plus/`
- `vault/sec-plus/` and `bench/sec-plus/` exist but are empty (structure just created)
- `.mlos/index.json` does not exist yet

**What's been decided but not yet built:**
- `ingest.py` — a script to scan inbox, move files to vault, and auto-populate the index
- The inbox→vault processing pipeline (scan, add, validate)
- Migration of `Sec+Analysis/` → `bench/sec-plus/`

**What's completed (Net+ side):**
- Full Net+ analysis methodology in `Docs/net+Analysis/` — this is reference material, not actively being worked on
- The methodology is being ported to Sec+ (see NetPlus_Recap.md for portability assessments)

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

### What you're likely here to do

The operator will tell you, but common tasks include:
- **Build `ingest.py`** — the inbox processing tool (scan, add, validate, export)
- **Process inbox items** — move files from `io/inbox/` → `vault/sec-plus/`, create index entries
- **Build bench artifacts** — Lab TOC, Trap Lab Filter, objective maps, MOCs
- **Run `moc.py`** — the existing MOC generator at `.mlos/moc.py`
- **Extend the tooling** — whatever the system needs next

### Before you start working

1. Read `CLAUDE.md`
2. Read `.mlos/DRAFT_index_schema_and_workflow.md` (especially sections 2 and 3)
3. Check if `.mlos/index.json` exists — if not, that's likely your first job
4. Run `git status` to see where things stand
5. Ask the operator what they want to focus on
