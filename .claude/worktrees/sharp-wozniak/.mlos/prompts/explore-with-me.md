# Claude-Cowork-Vault — Exploration Session

You are joining a knowledge management system under development. Before doing anything, orient yourself.

## Step 1: Read the landscape

Read these files in order:
1. `CLAUDE.md` — System overview and ground rules
2. `.mlos/DRAFT_index_schema_and_workflow.md` — The design doc (index schema, processing pipeline, query tooling)
3. `.mlos/moc.py` — The MOC generator tool (understand what it does, don't run it yet)

## Step 2: Map the current state

After reading, produce a brief status report:
- What's been built (directory structure, tools, prompts)
- What's been designed but not yet implemented (ingest.py, index, enrichment)
- What gaps exist (missing tools, incomplete docs, disconnected pieces)

## Step 3: Explore with me

Now we work together. Start by telling me:
1. What you found most interesting or unusual about the system design
2. Where you see the biggest gaps between the design doc and what actually exists
3. What you'd want to build first if this were your project

Then ask ME what I want to focus on. Don't assume — I might want to work on something you didn't expect.

## Tools available

- **MOC Generator:** `python .mlos/moc.py <directory> [-o] [--depth N]` — Scans a directory and builds a Map of Content
- **Git:** Repo is tracked, always pull before changes, commit after

## Ground rules

- Do NOT modify any files without asking me first
- Do NOT run scripts without showing me what they'll do
- Read first, understand second, suggest third, act only when I say go
- If you're unsure about something, ask — don't guess
