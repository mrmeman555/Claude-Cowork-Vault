# Use Case: Intelligent Watcher Agents for Context Maintenance

## What We Are Building

**ML OS (Meta-Language Operating System)** is a framework for building AI-powered knowledge management systems. The core product is a **vault system** -- a git-backed repository of curated document collections ("vaults") that AI agents can read from, write to, and maintain.

The system is operated primarily through **Claude Code** (Anthropic CLI agent) and **Claude Cowork** (Anthropic multi-agent collaboration interface). There is no separate chat UI -- Claude IS the interface. A local web server provides a visual browser for vault contents.

### Architecture

```
Storage layer:     Git repository (vault files + index.json)
System layer:      .mlos/ directory (Python CLI tools, agent configs, prompts)
AI layer:          Claude Code / Claude Cowork (reads, writes, executes)
Visual layer:      Local web server (vault browser at localhost:3001)
```

### What Exists Today

1. **Vault structure**: `vault/{project}/` for stored materials, `bench/{project}/` for work products, `io/inbox/` for new file intake, `.mlos/` for system tooling.

2. **Ingest pipeline** (`.mlos/ingest.py`):
   - `scan` -- preview inbox contents
   - `add` -- move files from inbox to vault with auto-indexing
   - `write` -- AI agents write directly to vault (bypasses inbox)
   - `view` -- query index by project/type
   - `check` -- validate index vs filesystem integrity
   - `export` -- render index as markdown

3. **Index** (`.mlos/index.json`): Tracks all vault items with id, filename, type, size, title, ingested date, project, and source (agent vs inbox).

4. **Context packs**: A vault project (`mlos-dev`) containing files that orient any new Claude session:
   - `project-state.md` -- what exists, current status
   - `decisions.md` -- architectural decisions with rationale
   - `session-history.md` -- distilled session summaries
   - `pickup.md` -- instructions for loading the context pack

5. **Vault browser**: Python HTTP server + vanilla HTML/CSS/JS UI for visual inspection of vault contents.

6. **ML OS template system** (separate repo): YAML-based agent prompt composition (kernel + schema + scenario -> full system prompt).

## The Problem: Context Rot

The context pack files go stale immediately. `project-state.md` says "Index: empty" but the index has 4 items. After a few sessions of active development, the gap between the context files and reality becomes a liability -- new sessions load outdated information and make wrong assumptions.

**Current workflow failure mode:**
1. Agent does work (writes files, makes decisions, builds tools)
2. Agent is supposed to update context files at end of session
3. Agent forgets, runs out of context, or session ends unexpectedly
4. Next session loads stale context pack
5. New agent has wrong picture of project state

**Root cause:** Context maintenance is a manual task that depends on the agent remembering to do it. Any system that requires a participant to "remember" something will eventually fail.

## What We Need: Intelligent Watcher Agents

We need **background agents that automatically maintain context** by observing what happens and updating the relevant files. The agent doing the work should never have to think about context maintenance -- it just works, and watchers keep the context fresh.

### Two Tiers of Maintenance

**Tier 1 -- Mechanical (no LLM needed):**
Regenerating files from deterministic data sources. These are simple scripts triggered by events.

- `project-state.md`: Regenerate from filesystem scan + index.json + git remote info. Everything in this file can be derived from the current state of the repo.
- Integrity checks: Validate index matches filesystem after any vault operation.
- Event logging: Append structured entries to a log when files are created, ingested, or modified.

**Tier 2 -- Intelligent (LLM required):**
Understanding WHAT happened and WHY, then expressing it in context files. This requires an AI to read raw signals and produce meaningful summaries.

- `session-history.md`: Read conversation transcripts + git log + event log, then distill into structured session summaries.
- `decisions.md`: Detect when architectural decisions are made during conversations and extract them into the decision log format.
- Anomaly detection: Notice when the vault state is inconsistent with expectations and flag it.

### Trigger Mechanisms (Options to Evaluate)

We need to determine the best way to trigger these watcher agents. Options:

1. **Claude Code hooks**: Shell commands that fire in response to Claude Code tool events (file writes, bash commands, etc.). Configured in Claude Code settings. Could trigger maintenance scripts automatically after work is done.

2. **Git hooks**: `post-commit`, `pre-push`, etc. Fire after git operations. Could trigger context regeneration after every commit. Limited to git events only.

3. **Python file watcher (watchdog)**: Background daemon process that monitors filesystem changes. Could react to any file modification in the vault. Requires a running process.

4. **Claude API calls from scripts**: Python scripts that call the Anthropic API directly (`anthropic.Anthropic().messages.create()`) to perform intelligent analysis. Small, scoped, cheap. No full conversation needed -- just focused prompts with specific context.

5. **Claude Agent SDK**: Anthropic SDK for building custom agents. Could potentially create persistent agent processes that monitor and react.

6. **OpenClaw/GitClaw**: Docker-based AI agent framework. User has a working setup already. Heavier solution but potentially more capable for persistent background agents.

7. **Claude Cowork automation**: If Cowork supports triggering agents programmatically or on schedules, this could be the most native solution.

### Structured Output as Enabler

A key enhancement: if Claude conversational outputs included **structured JSON metadata** alongside natural language, watcher agents could parse machine-readable signals instead of interpreting prose.

Example: Instead of a watcher reading "I decided to use git as the storage layer because..." and trying to extract the decision, Claude would also emit:

```json
{
  "event_type": "decision",
  "id": "D-006",
  "title": "Git as Primary Storage",
  "rationale": "Already working, version history free, multi-device via pull",
  "alternatives_rejected": ["home web server as primary"],
  "tags": ["storage", "architecture"]
}
```

This makes conversations ingestable by downstream AI without expensive NLP. The conversation becomes a **structured event stream** that watchers can process programmatically.

Relevant Anthropic features to investigate:
- Claude structured output / JSON mode capabilities
- Whether Claude Code supports custom output formats or hooks on output
- Whether conversation transcripts can include structured metadata
- Tool use patterns that naturally produce structured side-effects

## Implementation Requirements

### Must Have
- Tier 1 maintenance: `project-state.md` auto-regenerated from truth sources (filesystem + index)
- Event log: Append-only structured log of vault operations (already partially exists in index.json timestamps)
- A trigger mechanism that fires automatically -- zero manual intervention

### Should Have
- Tier 2 maintenance: AI-powered session history and decision extraction
- Structured output format for Claude interactions that watchers can parse
- Conversation transcript archival in the vault itself

### Nice to Have
- Real-time watchers (not just post-event hooks)
- Cross-session memory that does not depend on CLAUDE.md or auto-memory
- Watcher agents defined as ML OS scenarios (kernel + schema + watcher-scenario YAML)

## Key Questions for Research

1. What are Claude Code hook capabilities? What events can trigger hooks? Can hooks access the conversation context or just the tool parameters?

2. Does Claude Code or Claude Cowork support any form of background/scheduled agent execution?

3. What is the Claude Agent SDK model for persistent or event-driven agents? Can it create agents that watch and react rather than respond to prompts?

4. How does Claude structured output (JSON mode, tool_use) work, and can it be leveraged to produce machine-readable metadata alongside conversational output?

5. What patterns exist for "agentic workflows" in the Anthropic ecosystem that go beyond request-response?

6. How do Claude Code transcript files (.jsonl) work? Can they be programmatically accessed and processed by external scripts?

## Context for Prompt Design

The user (Mimir) wants to create a prompt for a **Claude documentation agent** -- an agent that will research Anthropic documentation and capabilities to answer the questions above. The prompt should instruct the agent to:

1. Research Claude Code hooks, settings, and extensibility
2. Research Claude Agent SDK capabilities for persistent/event-driven agents
3. Research Claude Cowork automation and multi-agent capabilities
4. Research structured output patterns (JSON mode, tool use, etc.)
5. Evaluate each option against the watcher agent requirements listed above
6. Produce a recommendation with concrete implementation steps

The goal is to find the lightest-weight, most native Anthropic solution before resorting to external frameworks like OpenClaw.
