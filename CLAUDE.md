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

## Linked Workspaces

This workspace is part of a multi-repo system. You have full file access to all of these — use absolute paths.

| Workspace | Path | What Lives There |
|-----------|------|-----------------|
| **Home_Lab_2026** (This Repo) | `C:\Users\Erinh\Desktop\Home_Lab_2026` | Vault infrastructure — `ingest.py` CLI pipeline, `server.py` API (port 3001), vault browser UI, per-project `tasks.json` tracking |
| **OpenClaw_Claude** (Shared Workspace) | `C:\Users\Erinh\Desktop\OpenClaw_Claude` | Engines, research, OpenClaw/NanoClaw architecture, operator profile (`mimir.md`), reflexivity system, Flow Mode. Git repo: `OpenClaw_Claude` |
| **ClaudeTest** (ML OS Demo) | `C:\Users\Erinh\Desktop\ClaudeTest` | ML OS visualization — boot sequence, dashboard, agent instantiation UI. Dev server on port 3000 |

### Key cross-repo files
- **OpenClaw pickup:** `C:\Users\Erinh\Desktop\OpenClaw_Claude\projects\openclaw\pickup.md`
- **Operator profile:** `C:\Users\Erinh\Desktop\OpenClaw_Claude\.context\mimir.md`
- **Engine prompts:** `C:\Users\Erinh\Desktop\OpenClaw_Claude\.context\engines\`
- **ML OS demo:** `C:\Users\Erinh\Desktop\ClaudeTest\index.html` (port 3000)

## Ground rules
- Do NOT modify vault files without asking the operator first
- Do NOT run scripts without showing what they'll do
- Read first, understand second, suggest third, act only when operator says go
