# Session History

> Distilled summaries of development sessions. Not a transcript — just the key threads, outcomes, and open questions.

---

## Session 1 — Foundation Build (2026-03-04/05)

**What happened:**
1. Started with the ML OS PDF (16-page framework doc) → built interactive web demo in ClaudeTest
2. Built `mlos.py` template composer (YAML kernel + schema + scenario → full system prompt)
3. Built `cowork.py` agent orchestration (registry, dispatch, shared memory, Living Doc Protocol)
4. Discovered Home_Lab_2026 repo — a CompTIA certification study project with 500+ files
5. Built `moc.py` MOC generator for Home_Lab_2026
6. User restructured Home_Lab_2026 into vault/bench/inbox architecture
7. Built `ingest.py` pipeline (scan, add, view, check, export)
8. Discussed frontend app concept — "eyes and hands" for Claude, not a chat replacement
9. User wants small, curated vaults with carefully selected items for specific purposes

**Key insight from user:** "I never edit notes by hand, it's all through AI. I think giving any AI the ability to create and store files within the system such that they can be retrieved later is what we should think about first."

**Open threads:**
- Frontend app design (vault browser, index dashboard, not started)
- ML OS agents designed to accompany vault docs (mentioned, deferred)
- Watcher/automation (discussed, deferred)
- Backfill of original Home_Lab_2026 content into vault (original files not present locally)

---

## Session 2 — Write Path & Context Packs (2026-03-05)

**What happened:**
1. Built `write` command for ingest.py — AI direct-to-vault path
2. Decided on git as storage layer, home server as future frontend host
3. Took full inventory of both projects
4. User identified biggest pain point: "reliably building sets of docs from different places"
5. User proposed context packs — curated vault projects that capture development state
6. Created `mlos-dev` vault project as the first context pack

**Key insight:** The ML OS project itself is the first real use case for the vault system. A context pack that captures state + decisions + history makes every new session productive immediately.

**Next priorities:**
- Populate the vault with real documents (the backend that reliably builds doc sets)
- Consider how context packs get loaded (pickup prompt, CLAUDE.md references, etc.)
- Everything else (frontend, agents, cowork integration) is downstream

---

## Session 3 — Vault Browser, Context Rot, Watcher Agents (2026-03-05)

**What happened:**
1. Built vault browser: `server.py` (Python HTTP server, port 3001) + `index.html` (dark terminal UI matching ML OS demo). API endpoints: `/api/index`, `/api/projects`, `/api/file`, `/api/tree`.
2. Fixed UTF-8 mojibake in all vault files caused by Windows stdin encoding mangling heredoc content. Built `fix_encoding.py`. Lesson: use Write tool directly, avoid bash heredocs for non-ASCII content on Windows.
3. Identified **context rot** as the core problem: context pack files go stale when agents forget to update them. Manual maintenance always fails eventually.
4. Designed **watcher agent architecture** (two tiers):
   - Tier 1 (Mechanical): Regenerate files from deterministic sources (filesystem + index). No LLM needed.
   - Tier 2 (Intelligent): Extract decisions, summaries from transcripts. Requires LLM.
5. Wrote comprehensive use case document (`usecase-watcher-agents.md`) covering requirements, 7 trigger mechanism options, and research questions.
6. Ran a Claude documentation agent to research native Anthropic capabilities (Claude Code hooks, Agent SDK, Cowork, structured output).
7. Found native tools insufficient for full watcher vision: PostToolUse hooks fire on ALL writes (not path-scoped), transcript access is broken (confirmed bug), hooks can't trigger other Claude conversations.
8. Built **Tier 1 `sync` command** in ingest.py: regenerates `project-state.md` from filesystem + index.json. Zero manual maintenance, reproducible, deterministic.

**Key insight:** The PostToolUse hook in Claude Code is too blunt for intelligent watcher agents. It fires on every write (not vault-scoped), is synchronous, per-machine (not per-project), and transcript semantic access is broken. Native Claude tools solve Tier 1 (mechanical) but not Tier 2 (intelligent).

**Open threads:**
- Tier 2 watcher agents: OpenClaw/GitClaw integration vs waiting for better native support
- Structured JSON output: embedding machine-readable metadata in conversation output for downstream AI parsing
- Populating the vault with real documents (user's stated biggest pain point)
- session-history.md and decisions.md still require manual (Tier 2) updates

**Next priorities:**
- Evaluate OpenClaw integration for persistent intelligent watcher agents
- Wire `sync` into git hooks or Claude Code PostToolUse hook for automatic Tier 1 maintenance
- Populate vault with real content beyond mlos-dev context pack
