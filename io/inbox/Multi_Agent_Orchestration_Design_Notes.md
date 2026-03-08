# Multi-Agent Orchestration: Self-Modifying Agents + Roundtable Methodology

> Design Notes — Captured from working session
> Date: 2026-02-06
> Status: **Pre-design thinking** — not yet scoped as a sprint
> Prerequisite Reading: ML_OS_Autopoiesis_Analysis.md, Python_Paradigm_Shift_Analysis.md, DeepResearch_Methodology_Packet.md

---

## The Core Idea

ML OS already has the building blocks for programmatic multi-agent orchestration with self-modifying capabilities. The convergence point is:

1. **Roundtable Methodology** (Deep Research Factory) — structured adversarial expert decomposition
2. **ML OS Agent Spawning** (§3.5 Scenario Handoff) — agents instantiate other agents inheriting the kernel
3. **Python Bootloader** — makes agent creation and governance programmatic
4. **Self-Modifying Context** — each spawned agent can edit its own `.mdc` rules and MASTER_CONTEXT

Combined, these produce a system where an orchestrator agent can analyze a problem, determine what expert perspectives are needed, spawn agents with tailored context, and let those agents refine themselves during execution.

---

## Building Blocks (Already Exist)

### 1. Roundtable Methodology — Task Decomposition Engine

From the Deep Research Factory: instead of asking a single model to simulate multiple experts, you *actually instantiate them* as separate agents.

**Key principle:** The problem itself determines what agents are needed. Not hardcoded roles — dynamic role generation.

**Methodology source:** `/mnt/share/IO/uploads/DeepResearch_Methodology_Packet.md`

Persona design principles:
- **Diversity of perspective** — each expert sees the problem through a different lens
- **Adversarial stance** — each expert REJECTS the obvious/shallow answer
- **Specific demands** — each expert demands a particular type of analysis
- **Cognitive model** — each expert thinks in a specific mental framework

### 2. ML OS Agent Spawning (§3.5)

The original V1 spec defines the lifecycle: *Design → Birth → Operation → Evaluation → Death/Promotion*

§3.5 Scenario Handoff: "The system should be capable of instantiating specialized agents that inherit the ML OS Core, the AI Schema, and a custom Scenario."

### 3. Python Bootloader — Programmatic Agent Factory

The bootloader can:
- Scan the problem space
- Compute what agents are needed
- Generate MASTER_CONTEXT files or `.mdc` rules for each
- Inject the right context packs
- Launch and manage lifecycle

### 4. Context Pack Infrastructure

The `publish_to_io.py` pipeline already creates Context Packets — this is an agent context compiler. Extend it for dynamic context pack assembly.

---

## Key Differentiator: Self-Modifying Agents

### Static Agents (Current Multi-Agent Frameworks)

```
Orchestrator creates context → Agent receives context → Agent works → Agent returns output
```

Agent is a consumer of its context. One-directional.

### Self-Modifying Agents (ML OS Vision)

```
Orchestrator creates initial context → Agent receives context → Agent works
    → Agent realizes it needs different context
    → Agent modifies its own .mdc rules / MASTER_CONTEXT / context pack
    → Agent reboots with updated context
    → Agent continues working with refined perspective
    → Agent returns output
```

Agent is a participant in its own configuration. Two-directional.

### What Self-Modifying Agents Can Do

| Action | Mechanism |
|--------|-----------|
| **Pull in more context** | Edit own `.mdc` rules to include additional file globs, or call context pack assembler |
| **Refine persona** | Modify own MASTER_CONTEXT to sharpen scenario — narrow focus, add discovered constraints |
| **React to sibling output** | Read another agent's output file, update own context to incorporate |
| **Escalate to orchestrator** | Write to shared signal file: "I need a capability I don't have — spawn a specialist" |

---

## Three Feedback Loops

### Loop 1: Self-Refinement (Agent ↔ Own Context)

```
Agent works → discovers framing is wrong →
  modifies own MASTER_CONTEXT →
  reboots with corrected perspective →
  produces better output
```

The autopoietic loop from the analysis — but at the *spawned agent* level. Every agent inherits ML OS's self-modification capability.

### Loop 2: Peer Influence (Agent ↔ Agent via shared workspace)

```
Agent A produces output → writes to shared folder →
  Agent B reads A's output → realizes conflict →
  Agent B modifies own context to account for A's findings →
  Agent B produces updated output addressing the conflict
```

Emergent inter-agent coordination without orchestrator micromanagement. Agents negotiate through artifacts.

### Loop 3: Upward Signal (Agent → Orchestrator)

```
Agent C realizes problem needs a perspective nobody has →
  Agent C writes request: "Need a Compliance Specialist" →
  Orchestrator reads request →
  Orchestrator runs Roundtable decomposition on sub-problem →
  Orchestrator spawns Agent D with right context →
  Agent D's output flows back to Agent C
```

System grows its own workforce based on what it discovers during execution.

---

## Orchestrator Pattern

```
┌─────────────────────────────────────────────┐
│           ORCHESTRATOR AGENT                 │
│  (ML OS Core + Roundtable Methodology)      │
│                                             │
│  1. Receives complex problem                │
│  2. Runs Roundtable decomposition:          │
│     "What 4-6 expert perspectives           │
│      would force the most rigorous          │
│      analysis of THIS problem?"             │
│  3. For each expert perspective:            │
│     → Generates a MASTER_CONTEXT            │
│     → Compiles a Context Pack               │
│     → Spawns an agent instance              │
│  4. Collects outputs                        │
│  5. Runs adversarial synthesis              │
│  6. Produces consolidated deliverable       │
└─────────────────────────────────────────────┘
         │           │           │
         ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Agent A │ │ Agent B │ │ Agent C │
    │ Expert  │ │ Expert  │ │ Expert  │
    │ Persona │ │ Persona │ │ Persona │
    │ 1       │ │ 2       │ │ 3       │
    │         │ │         │ │         │
    │ SELF-   │ │ SELF-   │ │ SELF-   │
    │ MODIFY  │ │ MODIFY  │ │ MODIFY  │
    │ CAPABLE │ │ CAPABLE │ │ CAPABLE │
    └────┬────┘ └────┬────┘ └────┬────┘
         │           │           │
         ▼           ▼           ▼
    ┌─────────────────────────────────────┐
    │     SYNTHESIS LAYER                 │
    │  Adversarial cross-examination      │
    │  → Consolidated output              │
    └─────────────────────────────────────┘
```

---

## Governance Requirements (The Hard Part)

### 1. Drift Boundaries

How far can an agent modify its own context before it's no longer the agent it was spawned to be?

**Solution:** Kernel immutability. ML OS Engine Core stays locked. Agent can modify its *scenario* and *supplemental context* (§1-S, §3), but not its *identity constants* (§1 core, §2 schema). Python bootloader enforces this — certain fields are read-only.

### 2. Infinite Recursion Prevention

Agent modifies context → reboots → modifies context → reboots → ...

**Solution:** Modification budget. Each agent gets N self-modification cycles (bootloader increments counter in agent's state file). After N modifications, agent must produce output or escalate.

### 3. Context Corruption Protection

Agent writes bad rules that break its own context window.

**Solution:** Bootloader validates every self-modification before applying. Schema check, token budget check, dependency check. Invalid modifications are rejected with an error message instead of a corrupted boot.

### 4. Coordination Conflict Resolution

Agent A and Agent B both modify a shared resource simultaneously.

**Solution:** File-level locking or shared message bus. Each agent owns its own context files exclusively. Shared communication through designated `_comms/` folder with append-only semantics.

---

## Proposed Workspace Structure

```
workspace/
├── _orchestrator/
│   ├── MASTER_CONTEXT.md          # Orchestrator's own context (self-modifiable)
│   ├── agent_registry.json        # What agents exist, their status
│   └── synthesis_queue/           # Outputs waiting for synthesis
│
├── _agents/
│   ├── agent_a/
│   │   ├── MASTER_CONTEXT.md      # Agent A's context (SELF-MODIFIABLE)
│   │   ├── rules/                 # Agent A's .mdc rules (SELF-MODIFIABLE)
│   │   ├── context_pack/          # Agent A's loaded context
│   │   ├── output/                # Agent A's deliverables
│   │   └── state.json             # Modification counter, status, health
│   ├── agent_b/
│   │   └── ...
│   └── agent_c/
│       └── ...
│
├── _comms/                        # Inter-agent communication
│   ├── broadcast/                 # Messages to all agents
│   ├── requests/                  # Escalation requests to orchestrator
│   └── peer/                      # Agent-to-agent messages
│
└── _bootloader/
    ├── boot.py                    # Computes prompts from live state
    ├── validator.py               # Validates self-modifications
    └── lifecycle.py               # Spawn, monitor, collect, terminate
```

---

## Biological Parallel: Immune System + Endocrine System

| ML OS Concept | Biological Analogue |
|---------------|-------------------|
| Each agent | Specialized immune cell (T-cell, B-cell, macrophage) |
| Self-modification | Cell differentiation (naive T-cell → killer T-cell on antigen encounter) |
| Peer influence via shared workspace | Cytokine signaling (chemical signals changing neighbor behavior) |
| Orchestrator spawning new agents | Bone marrow producing new immune cells for detected threats |
| Kernel immutability | DNA — every cell differentiates but shares the same genome |
| Modification budget | Apoptosis signals — cells that divide too many times without useful work get terminated |

---

## Implementation Dependencies

To build this, these must exist first:

1. **Python Bootloader** (core) — dynamic prompt computation from workspace state
2. **RuleManager API** (from Python_Paradigm_Shift_Analysis.md) — programmatic `.mdc` rule CRUD
3. **Context Pack Assembler** — extends `publish_to_io.py` for dynamic bundling
4. **Agent Template Compiler** — takes persona definition → generates valid MASTER_CONTEXT + rules
5. **Agent Lifecycle Manager** — spawn, monitor, collect, terminate
6. **Synthesis Protocol** — MASTER_CONTEXT for final synthesis agent

---

## Key Insight

> Self-modification isn't a feature you add to agents — it's the natural consequence of giving agents the same ML OS capabilities that the kernel agent already has. Every agent inherits the Engine Core. The Engine Core includes the self-development scenario. If you take that seriously, every spawned agent is *already* a self-modifying entity. The Python bootloader makes it safe. The governance layer makes it bounded.

---

## Status

**This is pre-design thinking.** The ideas are captured here for consideration. Before moving forward:

- Need to determine the right design path that scales fast with deliberate, smart choices
- Need to sequence dependencies (bootloader first? rules API first? orchestrator pattern first?)
- Need to decide scope — full vision vs. minimum viable orchestration
- A lot to consider before committing to implementation direction

*Captured: 2026-02-06*
