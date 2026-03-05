# CLAUDE.md — Claude-Cowork-Vault

## Repo
- **URL:** https://github.com/mrmeman555/Claude-Cowork-Vault.git
- **Branch:** main

## Structure

```
vault/          ← Stored, processed materials (organized by project)
bench/          ← Work product / analysis that references vault items
io/inbox/       ← Raw drop zone for new materials
.mlos/          ← System tools, index, prompts, memory
```

- `vault/{project}/` stores files. They go in, they don't change.
- `bench/{project}/` is where you build things from vault materials — MOCs, filters, maps.
- `io/inbox/` is the drop zone. Files leave when they're processed into vault.
- `.mlos/index.json` is the metadata index (source of truth for what's in the vault).

## Index Schema (minimal, auto-derived)

Each vault item gets: `id`, `filename`, `type`, `size`, `title`, `ingested`, `project`.
Richer metadata (tags, objectives, descriptions) added later in batches as needed.

## Workflow
1. `git pull` before doing anything
2. Commit after making changes
3. Push when done

## Who works here
- **Cloud agent (claude.ai / Cowork):** Writes docs, plans changes, commits to repo
- **Local agent (Claude Code):** Pulls repo, executes on the actual machines
- **Operator (Mimir):** Relays between agents, final authority

## Ground rules
- Do NOT modify vault files without asking the operator first
- Do NOT run scripts without showing what they'll do
- Read first, understand second, suggest third, act only when operator says go
