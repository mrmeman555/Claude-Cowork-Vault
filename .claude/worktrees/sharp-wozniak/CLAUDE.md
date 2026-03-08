# CLAUDE.md — Claude-Cowork-Vault

## Repo
- **URL:** https://github.com/mrmeman555/Claude-Cowork-Vault.git
- **Branch:** main

## What this is

A knowledge management system under development. This repo contains the **architecture, tooling, and prompts** — not the data itself. Study materials and analysis outputs live elsewhere; this repo is cloned and populated when deployed.

## Structure

```
vault/{project}/    Stored, processed materials (organized by project)
bench/{project}/    Work product that references vault items — MOCs, filters, maps
io/inbox/           Raw drop zone for new materials
.mlos/              System layer — index, tools, prompts, memory
```

- `vault/` and `bench/` mirror each other by project name.
- `io/inbox/` is the ingest point. Files leave when processed into vault.
- `.mlos/index.json` is the metadata index (source of truth for what's in the vault).
- `.mlos/prompts/` contains agent prompts for onboarding and exploration.
- `.mlos/moc.py` generates Maps of Content from directory scans.

## Index Schema (minimal, auto-derived)

Each vault item gets: `id`, `filename`, `type`, `size`, `title`, `ingested`, `project`.
Richer metadata (tags, objectives, descriptions) added later in batches as needed.
Paths are NOT stored — derived from `vault/{project}/{filename}`.

## What needs to be built

- `ingest.py` — scan inbox, move to vault, auto-populate index
- Index enrichment workflow — batch-add metadata fields
- Query/export tooling — filtered views, rendered INDEX.md

## Workflow
1. `git pull` before doing anything
2. Commit after making changes
3. Push when done

## Who works here
- **Cloud agent (claude.ai / Cowork):** Writes docs, plans changes, designs systems
- **Local agent (Claude Code):** Pulls repo, executes, builds tools, processes files
- **Operator (Mimir):** Relays between agents, final authority

## Ground rules
- Do NOT modify vault files without asking the operator first
- Do NOT run scripts without showing what they'll do
- Read first, understand second, suggest third, act only when operator says go
