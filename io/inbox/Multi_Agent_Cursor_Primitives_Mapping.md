# Multi-Agent Cursor Primitives → ML OS Architecture Mapping

> **Date:** 2026-02-07
> **Source:** Conversation between operator and Meta Agent
> **Related Tasks:** ID:172 (BUILD: Message Enrichment Pipeline), ID:170 (Watcher Agent), ID:171 (Enrichment Design), ID:154 (Research Cursor multi-agent orchestration), ID:156 (Research inter-agent communication)
> **Tags:** multi-agent, MCP, subagents, parallel-agents, architecture, implementation-path

---

## Part 1: Research — Cursor Multi-Agent Capabilities (Operator)

### Context

The operator has been planning to implement MCP servers, multi-agent workflows, subagents, and parallel agents. The following is a synthesis of research into Cursor's native multi-agent primitives.

---

### Making AI Agents Collaborate in Cursor

In Cursor, AI agents do not "talk" to each other directly in a conversational, real-time manner. Instead, collaboration is achieved through three distinct architectural patterns: competitive parallel work, hierarchical task delegation, and shared external tools. The SpecStory extension enhances these workflows by creating a persistent, version-controlled log of the prompts and AI interactions, providing a form of asynchronous, readable context for both humans and other agents.

| Approach | Communication Style | How It Works | Best For |
|---|---|---|---|
| Parallel Agents | Competitive & Indirect | Multiple agents work on the same task in isolated git worktrees. You review their solutions and merge the best one. | Solving a complex problem with multiple possible solutions or comparing different AI models on the same task. |
| Subagents | Hierarchical Delegation | A primary agent assigns specialized, isolated sub-tasks to subordinate agents and receives a summary of the results. | Breaking down a large, multi-step task (e.g., coding, testing, documenting) into parallel or sequential workstreams. |
| MCP Servers | Mediated & Asynchronous | Agents interact with a custom-built external tool (the server) that can manage a shared state or message queue. | Creating sophisticated workflows where agents need to share information or trigger actions based on each other's progress. |

### The Role of SpecStory: Creating a Shared Memory

SpecStory automatically captures every AI conversation — prompts, reasoning, code generated — and saves it as a Markdown file within the project in a `.specstory/history/` directory.

This creates a persistent, human-readable, and version-controlled memory of every interaction:

- **Asynchronous Context:** An agent in a new session can't "see" what another agent is doing live. However, you can provide it with the context of a previous agent's work by pointing it to the relevant SpecStory Markdown file (e.g., using `@` mentions). The agent can then read the log to understand the history, design decisions, and trade-offs of a previous task.
- **Audit Trail:** It provides a definitive log of which agent did what, including which subagents were called or which MCP tools were used. Invaluable for debugging complex multi-agent workflows.
- **Source of Truth:** SpecStory treats the natural language prompt as the true source code, meaning the intent behind the code is always preserved alongside the code itself.

**In essence, SpecStory doesn't create a "chat room" for agents. It creates a library of their past work that can be referenced, providing a robust foundation for more complex, multi-step development processes.**

### Parallel Agents: Collaboration Through Competition

Built-in method for running multiple agents simultaneously to tackle the same problem. Communication is indirect; they don't coordinate during the task but instead present competing solutions.

**Technical Implementation — Git Worktrees:**

1. **Initiation:** You give a single prompt to multiple agents or models at once.
2. **Isolation:** Cursor automatically creates a new, separate worktree for each agent. Each agent gets its own folder and branch, so its file edits, terminal commands, and tests don't interfere.
3. **Execution:** Each agent works independently. You can configure setup scripts in a `.cursor/worktrees.json` file to automatically run commands like `npm install` or `pip install -r requirements.txt` in each worktree before the agent begins.
4. **Review:** Once complete, Cursor presents each agent's solution in a card-based view with diffs.
5. **Selection:** You choose the best solution and click "Apply." Cursor merges the changes from that agent's worktree into your main working branch.

**Practical Uses:**
- Model comparison (Claude vs GPT vs others on the same prompt)
- Complex refactoring (multiple approaches, weigh trade-offs)
- Generating alternatives (e.g., multiple UI implementations)

### Subagents: Collaboration Through Hierarchical Delegation

Not peer-to-peer communication — a parent agent delegating tasks to specialized "employees." Clear hierarchy, keeps the main conversation focused.

**Technical Implementation — `.cursor/agents/` directory:**

Subagents are defined as simple Markdown files with YAML frontmatter:

- `name`: Unique identifier used to call the subagent (e.g., `/verifier`)
- `description`: Critical field that tells the parent agent *when* to use this subagent. Good description enables automatic delegation.
- `model`: Specifies which AI model to use (e.g., faster/cheaper model for simple tasks)

**Communication Flow:**
1. Parent agent encounters a complex task or is told to use a subagent
2. Sends a prompt with all necessary context to the subagent (subagents start with a clean slate — no access to parent's conversation history)
3. Subagent works autonomously in its own isolated context window
4. Returns a final message with results to the parent

**Practical Use — Feature Development Workflow:**
- Parent receives: "Add a password reset feature"
- Delegation 1: `/code-explorer` subagent finds all relevant auth files
- Delegation 2: Implementer subagent writes the code
- Delegation 3: `/test-runner` subagent runs tests
- Delegation 4: `/verifier` subagent skeptically checks the implementation

### MCP Servers: Collaboration Through a Shared Brain

Most flexible and powerful — also most technically complex. Allows agents to interact with external tools, including tools specifically designed as communication bridges.

**Technical Implementation — Custom MCP Server:**

An MCP server exposes custom tools that Cursor agents can call. To make agents "talk," build a server that manages shared state (message queue, key-value store, database).

**Example — "Message Bus" MCP Server:**
1. **The Server:** Two primary tool functions:
   - `sendMessage(recipient_agent, message_content)`: Stores a message for a specific agent
   - `checkMessages(agent_name)`: Retrieves all messages addressed to that agent and clears them
2. **Agent A's Turn:** Makes MCP call: `sendMessage("Agent B", "Please refactor UserService.ts")`
3. **Agent B's Turn:** Calls `checkMessages("Agent B")` → receives the message → performs the task

**Practical Uses:**
- **Stateful Workflows:** Migration agent sets a "migration_complete" flag; deployment agent checks it before proceeding
- **Shared Knowledge Base:** Research agent documents API endpoints; other agents query the KB
- **Distributed Problem Solving:** Frontend and backend agents notify each other of contract changes

---

## Part 2: ML OS Architecture Mapping (Meta Agent Analysis)

### How Cursor's Multi-Agent Primitives Map to ML OS

| ML OS Component | Cursor Primitive | Implementation |
|---|---|---|
| **ML OS Kernel** (agent grounding) | **Subagent** (`.cursor/agents/`) | Each ML OS agent type becomes a subagent definition — YAML frontmatter sets the model, description triggers auto-delegation, body IS the kernel prompt |
| **Message Enrichment Pipeline** | **MCP Server** | A custom MCP server that exposes `enrichContext(message)`, `queryTasks(sprint)`, `getSnapshot(messageId)` — agents call it like any tool |
| **Nervous System Watcher** | **MCP Server** (background) | Same or companion MCP server tailing `.specstory`, writing to SQLite, exposing `getRecentDecisions()`, `getRelatedMessages(intent)` |
| **Context Snapshot Store** | **MCP Server** (data layer) | `storeSnapshot(enrichment_data)` and `querySnapshots(filter)` — every agent can read/write to the shared memory |
| **Grounding Heartbeat** | **Subagent** | A `/grounding-check` subagent that the parent calls every N turns to re-anchor — returns compressed kernel state |
| **Deep Research / Roundtable** | **Parallel Agents** | Competing expert analyses via git worktrees — you pick the best synthesis |
| **Transcript as Spine** | **SpecStory** (already exists) | The append-only event log. Already working. The MCP server just makes it queryable. |

### The Key Realization

You don't need to build the entire ML OS runtime from scratch in Python. **Cursor already has the multi-agent infrastructure** — you just need to wire ML OS concepts into it:

1. **Subagents = ML OS Agent Types.** The `.cursor/agents/` directory with Markdown + YAML frontmatter is literally the mechanism for defining grounded agents. Each agent definition file IS a kernel + scenario prompt. The `description` field enables automatic delegation ("when the parent encounters a grounding task, call `/grounding-check`").

2. **MCP Server = The Nervous System.** Instead of a standalone Python daemon, the enrichment pipeline and watcher could be an MCP server that Cursor agents call as tools. The agent says "enrich this context" → MCP server queries TaskEngine, Index DB, recent .specstory → returns structured context. Same architecture, but agents pull from it on demand instead of having it pushed via `active_context.mdc`.

3. **Both approaches can coexist.** The MCP server handles on-demand queries (agent asks for context). The `active_context.mdc` rule handles always-on injection (context pushed every turn). Push + pull.

### The Architecture

```
                    ┌─────────────────────────┐
                    │  .cursor/agents/        │
                    │  ├── ml-os-kernel.md     │  ← Subagent definitions
                    │  ├── grounding-check.md  │     (ML OS agent types)
                    │  ├── task-extractor.md   │
                    │  └── research-expert.md  │
                    └────────────┬────────────┘
                                 │ delegates to
                    ┌────────────▼────────────┐
                    │  Parent Agent (Cursor)   │
                    │  Reads: active_context   │  ← Push (always-on rule)
                    │  Calls: MCP tools        │  ← Pull (on-demand)
                    └────────────┬────────────┘
                                 │ MCP tool calls
                    ┌────────────▼────────────┐
                    │  ML OS MCP Server        │
                    │  (Node.js or Python)     │
                    │                          │
                    │  Tools:                  │
                    │  • enrichContext()        │
                    │  • queryTasks()           │
                    │  • getSnapshots()         │
                    │  • getRelatedMessages()   │
                    │  • storeDecision()        │
                    │                          │
                    │  Backends:               │
                    │  ├── TaskEngine (SQLite)  │
                    │  ├── Context Snapshots    │
                    │  ├── .specstory watcher   │
                    │  └── File index           │
                    └─────────────────────────┘
```

### What This Changes

The Message Enrichment Pipeline design doc assumed a **file-based approach** — a Python process writing to `active_context.mdc`. That still works. But now there's a second path:

- **File-based (push):** External process → writes Cursor rule → agent reads it automatically. Simple, no code on the agent side.
- **MCP-based (pull):** Agent → calls MCP tool → gets enriched context on demand. More flexible, agent can ask specific questions.

**The smart play is both.** The MCP server runs the enrichment logic. It also writes `active_context.mdc` as a side effect. Agents that support MCP get the full tool suite. Agents that don't (or simpler workflows) still get the always-on context injection via rules.

### Practical Next Steps

The `.cursor/agents/` subagent approach is the fastest win — defining ML OS agent types as subagent Markdown files. The MCP server is the bigger build but gives the full Nervous System.

---

## Connections

- **Supersedes:** This mapping refines the implementation strategy in [Message_Enrichment_Pipeline_Design.md](./Message_Enrichment_Pipeline_Design.md) — the MCP server becomes the primary runtime, with file-based injection as a fallback.
- **Extends:** [Multi_Agent_Orchestration_Design_Notes.md](./Multi_Agent_Orchestration_Design_Notes.md) — those pre-design notes now have concrete implementation primitives.
- **Implements:** [Engine_Core_MASTER_CONTEXT_Spec.md](./Engine_Core_MASTER_CONTEXT_Spec.md) — the Kernel/MASTER_CONTEXT separation maps directly to subagent definitions.
- **Enables:** [Drift_Recalibration_Design.md](./Drift_Recalibration_Design.md) — the Grounding Heartbeat can be a subagent called periodically.

*Captured: 2026-02-07, from live conversation during ML OS architecture session.*
