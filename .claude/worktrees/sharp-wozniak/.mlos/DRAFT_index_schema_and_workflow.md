# DRAFT — Index Schema & Processing Workflow (v2)

> **Status:** Draft for review — nothing has been changed in the repo.
> **Purpose:** Concrete proposal for the inbox → vault → bench pipeline.

---

## 1. Proposed Directory Layout

```
Home_Lab_2026/
  .mlos/
    index.json          ← THE source of truth (all metadata)
    moc.py              ← existing MOC generator
    ingest.py           ← NEW: processing script (moves + indexes)
    prompts/            ← existing
    memory/             ← agent memory (future use)
    output/             ← generated views / reports
    scenarios/          ← future use
  vault/
    sec-plus/           ← stored materials for the sec-plus project
    net-plus/           ← stored materials for the net-plus project
    (new projects get new folders as needed)
  bench/
    sec-plus/           ← work product / analysis for sec-plus
    net-plus/           ← work product / analysis for net-plus
  io/
    inbox/              ← raw drop zone (unchanged role)
    uploads/            ← existing
  CLAUDE.md
```

**Key principles:**
- `vault/` stores processed materials. Files go in, they don't change.
- `bench/` is where you build things that *reference* vault materials — MOCs, filters, maps, analyses.
- `io/inbox/` is the drop zone. Files leave when they're processed.
- Project folders in vault and bench mirror each other. A project is just a name for a body of work.

---

## 2. Index Schema (`.mlos/index.json`)

### The minimal, auto-derivable schema

Every field below can be populated by a script with zero human judgment.

```json
{
  "version": "1.0",
  "last_updated": "2026-03-05T19:30:00Z",
  "items": [
    {
      "id": "a7f3",
      "filename": "SecPlusLM_8e_Lab04-2.docx",
      "type": "docx",
      "size": 35000,
      "title": "Lab 04-2",
      "ingested": "2026-03-05",
      "project": "sec-plus"
    },
    {
      "id": "b2e1",
      "filename": "CompTIA-Security-Plus-SY0-701-Exam-Objectives.pdf",
      "type": "pdf",
      "size": 1250000,
      "title": "CompTIA Security+ SY0-701 Exam Objectives",
      "ingested": "2026-03-05",
      "project": "sec-plus"
    },
    {
      "id": "c9d4",
      "filename": "Cengage_ExamObjectives_DeepResearch.md",
      "type": "markdown",
      "size": 45200,
      "title": "A Data-Driven Study Framework for the CompTIA Security+ SY0-701 Exam",
      "ingested": "2026-03-05",
      "project": "sec-plus"
    },
    {
      "id": "d5a8",
      "filename": "Good_Reddit_Post.md",
      "type": "markdown",
      "size": 12400,
      "title": "Passed Sec+, Was So EZ I Am Beyond SHOCKED — Ultimate Study Guide",
      "ingested": "2026-03-05",
      "project": "sec-plus"
    },
    {
      "id": "e1b7",
      "filename": "professor-messer-sy0-701-comptia-security-plus-course-notes-v106.pdf",
      "type": "pdf",
      "size": 8500000,
      "title": "Professor Messer SY0-701 Course Notes v1.06",
      "ingested": "2026-03-05",
      "project": "sec-plus"
    }
  ]
}
```

### Schema field explanations

| Field | Type | How it's derived | Purpose |
|-------|------|-----------------|---------|
| `id` | string | Auto-generated (short hash of filename + ingested date) | Unique identifier |
| `filename` | string | From filesystem | The file's name |
| `type` | string | From file extension (reuses moc.py logic) | What kind of file |
| `size` | int | From filesystem | File size in bytes |
| `title` | string | Auto-extracted: first `#` heading in .md, docstring in .py, filename heuristic for .docx (reuses moc.py logic) | Human-readable name |
| `ingested` | string | Timestamp at processing time | When it entered the vault |
| `project` | string | Matches the vault subfolder the file lands in | Which body of work this belongs to |

### What's intentionally left out (for now)

These fields are all valuable but require human judgment. They get added **later, in batches**, when a specific task demands them:

| Future field | When you'd add it | What triggers the batch |
|-------------|-------------------|------------------------|
| `tags` | When you need to filter/query across items | Building the Trap Lab Filter, or any cross-cutting analysis |
| `objectives` | When you need to map items to exam objectives | Running the Verb Cipher / objective coverage analysis |
| `source` | When you need to know provenance or sanitization rules | Public repo packaging, deciding what can be referenced |
| `blooms_level` | When you need cognitive tier data | Trap Lab Filter specifically |
| `description` | When an agent or human has actually read the item | Any deep analysis pass |
| `notes` | Anytime | Freeform, accumulates over time |
| `references` | When building relationship maps between items | MOC generation, dependency analysis |

The schema grows as needs arise. The index file just gains new keys on items that have been enriched. Items without a given key simply don't have that metadata yet — that's fine.

### Path resolution

**No path is stored in the index.** A file's location is derived:

```
vault/{project}/{filename}
```

This means:
- Files never have stale paths in the index
- If you rename a project folder, you update the `project` field (one find-replace), not individual paths
- A simple lookup function resolves any item: `get_path(item) → vault/{item.project}/{item.filename}`

**Tradeoff:** This requires filenames to be unique *within a project*. If two files with the same name land in the same project, one gets renamed at ingest time (e.g., `README.md` → `README_ryanliupie.md`). The `ingest.py` script handles this automatically.

---

## 3. Processing Workflow

### Ingest (inbox → vault)

```
1. Operator drops files in io/inbox/
2. Run: python .mlos/ingest.py scan io/inbox/
   → Lists all files not yet in the index
3. Run: python .mlos/ingest.py add io/inbox/<file-or-folder> --project sec-plus
   → For each file:
     a. Derives the 6 metadata fields automatically
     b. Checks for filename collision in vault/{project}/
     c. Moves file from inbox → vault/{project}/
     d. Appends entry to index.json
   → For folders: processes all files inside, then removes the empty folder
4. No human input needed beyond choosing the project name
```

### Enrich (batch metadata updates — future)

```
1. Run: python .mlos/ingest.py enrich --project sec-plus --field tags
   → Walks all items in the project
   → For each item, proposes tags (agent or human)
   → Updates index.json entries
   → Can be interrupted and resumed (tracks which items already have the field)
```

### Query (finding things)

```
# List everything in a project
python .mlos/ingest.py view --project sec-plus

# Filter by type
python .mlos/ingest.py view --project sec-plus --type docx

# Export a human-readable index
python .mlos/ingest.py export --project sec-plus > bench/sec-plus/INDEX.md

# Future (after enrichment): filter by tag, objective, etc.
python .mlos/ingest.py view --tag lab --project sec-plus
```

### Validate (keep index honest)

```
python .mlos/ingest.py check
→ For every item in index.json:
  - Does vault/{project}/{filename} exist?
  - Are there files in vault/ NOT in the index? (orphans)
  - Any duplicate filenames within a project?
```

---

## 4. How bench/ references vault/

Bench files are your analysis artifacts — Lab TOCs, Trap Lab Filters, objective maps, MOCs. They reference vault items by ID or by relative path:

```markdown
<!-- vault-refs: a7f3, b2e1 -->

Lab 04-2 covers [Exploring Certification Authorities](../../vault/sec-plus/SecPlusLM_8e_Lab04-2.docx)
and maps to objective 1.4 per the [official objectives](../../vault/sec-plus/CompTIA-Security-Plus-SY0-701-Exam-Objectives.pdf).
```

The HTML comment is machine-parseable for future validation tooling.

---

## 5. What This Enables

**Immediately (with just the 6-field index):**
- Know exactly what materials you have, per project
- Auto-generate a manifest / INDEX.md for any project
- Detect orphan files, missing items, duplicates
- Give any agent instant orientation by reading index.json

**After enrichment batches:**
- Trap Lab Filter (needs: tags + objectives + blooms_level on lab items)
- Objective Coverage Map (needs: objectives on all items)
- Source Audit (needs: source.proprietary flag)
- Smart MOCs with descriptions and cross-references

---

## 6. Suggested First Steps

1. Create `vault/sec-plus/` and `bench/sec-plus/`
2. Build `ingest.py` with `scan` and `add` commands
3. Process the 5 simple inbox items first (the markdown files + PDFs at top level)
4. Batch-process the 74 lab .docx files
5. Move existing `Sec+Analysis/` content into `bench/sec-plus/`
6. Move existing `Docs/net+Analysis/` content into `bench/net-plus/` (optional backfill)

---

## 7. Open Questions

1. **Backfill Net+?** The Net+ materials are already organized in `Docs/net+Analysis/`. Move them into the vault/bench structure, or leave them as-is for now?
2. **The ryanliupie repo** has its own internal structure (quizzes, notes, PBQs). Index each file individually, or keep the folder structure inside `vault/sec-plus/ryanliupie/` as a sub-project?
3. **Lab_TOC.md** — it's an analysis artifact (bench material), not a raw file. Move it to `bench/sec-plus/` now?
4. **ID generation** — short hash (like `a7f3`) or sequential with project prefix (like `sp-001`)? Hash is collision-resistant but opaque. Sequential is readable but breaks if items are added out of order.
5. **Existing Sec+Analysis/ and Docs/net+Analysis/** — rename/move to `bench/` now, or defer until the system is proven?
