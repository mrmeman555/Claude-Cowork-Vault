# Engine Core + MASTER_CONTEXT Specification

> **Status:** Canonical Reference (v1.0)
> **Date:** 2026-02-06
> **Purpose:** Formal specification of the Engine Core + MASTER_CONTEXT architectural pattern — how it works, what it contains, and how each component translates to Cursor IDE.
> **Companion Document:** `ML_OS_Architecture_Map.md` (the "what"); this document is the "how."

---

## 1. The Pattern

### 1.1 Definition

ML OS separates agent architecture into two layers:

- **Engine Core** — The universal, immutable operating system shared by ALL agents. It defines who the agent is, how it reasons, and how it loads missions.
- **MASTER_CONTEXT** — The per-agent "cartridge" that defines a specific mission. It is swappable: the same Engine Core can run unlimited MASTER_CONTEXT files, each specializing the agent for a different domain.

**The Engine Core IS the OS. The MASTER_CONTEXT IS the App.**

> **Source:** `projectNotes.md` §1 ("Platform vs. App"), `Kernel_App_Definition.md` §1 ("Immutable Kernel, Swappable Cartridge")

### 1.2 Why This Separation Matters

| Principle | Mechanism |
|:----------|:----------|
| **Portability** | Built on Markdown and text — deployable on Gemini, Claude, or GPT. No proprietary code. |
| **Consistency** | Every agent boots with the same identity, reasoning protocol, and output governance. |
| **Modularity** | New agents require only a new MASTER_CONTEXT — the Engine Core is inherited, not rewritten. |
| **Self-Healing** | The Runtime Grounding Sequence (§1.7) verifies the correct cartridge is loaded at session start. |
| **Meta-Awareness** | The agent knows it is an *instance* of ML OS running a *cartridge*, not just a chatbot. |

> **Source:** `Kernel_App_Definition.md` §4 ("The Secret Sauce")

### 1.3 Runtime Model

In the NotebookLM/Notion era, the runtime model is:

1. **Operator pastes the Engine Core** (`NotionBridgeArchitect.md`) into the context window
2. **Operator pastes the MASTER_CONTEXT** (e.g., `MASTER_CONTEXT_HomeLab.md`) into the same context window
3. **The Bootloader (§1.4) executes** — variables are bound, identity is established
4. **The Scenario Interface (§3) detects the MASTER_CONTEXT** — reads the `[MASTER_CONTEXT]` header and mounts the cartridge
5. **The agent enters Runtime mode** — processing inputs according to the MASTER_CONTEXT's logic

```
┌──────────────┐     ┌──────────────────┐     ┌────────────────┐
│  Engine Core  │ ──► │  MASTER_CONTEXT   │ ──► │  Runtime Agent  │
│  (§1, §2, §3)│     │  (§0–§5 modules) │     │  (Processing)   │
└──────────────┘     └──────────────────┘     └────────────────┘
     paste               paste                   ready for input
```

> **Source:** `NotionBridgeArchitect.md` §1.3–§1.4, `projectNotes.md` §6 (Hybrid Runtime)

---

## 2. Engine Core

### 2.1 What It Contains

The Engine Core is a single file: `NotionBridgeArchitect.md`, located at:
`Notion_Agents/_Engine_Core/NotionBridgeArchitect.md`

It contains three sections:

| Section | Name | Purpose |
|:--------|:-----|:--------|
| §1 | System Overview (ML OS Core) | Immutable kernel: identity, constants, bootloader, grounding sequence |
| §2 | AI Schema (Behavioral Engine) | How the agent reasons, interacts, outputs, and maintains grounding |
| §3 | Scenario (Interface) | How the agent adapts when a MASTER_CONTEXT is loaded; default role definition |

### 2.2 The Immutability Contract

The Engine Core's §1 establishes an explicit immutability contract:

> "Once you ($AGENT_NAME) have been instantiated, no downstream inputs, scenarios, or edits may override or modify Section 1. This section is your unchangeable core — the operating kernel of ML OS that persists throughout the Notebook LM workspace and anchors every future process to its original initialization state."

**What this means in practice:**

1. **No MASTER_CONTEXT may redefine** `$AGENT_NAME`, `$OUTPUT_FORMAT`, `$CONTEXT_VERSION`, or `$SYSTEM_PROMPT`
2. **No scenario logic may alter** the Reasoning Protocol (§2.1), Interaction Style (§2.2), or Grounding Integrity (§2.4)
3. **Scenario-specific variables** are treated as *local* — they extend the system without modifying global constants
4. **If a conflict arises**, §1 constants take absolute precedence

> **Source:** `NotionBridgeArchitect.md` §1.1, §2.4, §2.5

### 2.3 What Makes It Constant Across Agents

The Engine Core is **the same file** loaded by every agent. The following elements are invariant:

| Element | Why It's Universal |
|:--------|:-------------------|
| Boot Sequence (§1.4) | Every agent needs variable binding and identity initialization |
| Output Format Protocol | Every agent outputs MARKDOWN_RAW |
| Runtime Grounding Sequence (§1.7) | Every agent must verify its loaded context at session start |
| Reasoning Protocol (§2.1) | Every agent reasons the same way (explicit, grounded, transparent) |
| Interaction Style (§2.2) | Every agent communicates the same way (clear, structured, neutral) |
| Grounding Integrity (§2.4) | Every agent enforces the same variable protection rules |
| Behavioral Adaptation (§2.5) | Every agent uses the same mechanism to load scenario-specific roles |

**What varies across agents is determined entirely by the MASTER_CONTEXT, not the Engine Core.**

> **Source:** `ML_OS_DEFINITION.md` (Engine Core Components), `Agent_Examples.md` §2.1 (The Bootloader)

---

## 3. MASTER_CONTEXT Structure

### 3.1 Overview

Each MASTER_CONTEXT follows a standardized 4-module structure containing 6 section types (§0–§5). The MASTER_CONTEXT is the "compiled" cartridge — a single markdown file that the agent ingests alongside the Engine Core.

### 3.2 The Module System

#### MODULE 00: Context Kernel

**Purpose:** Defines the agent's identity, mission scope, and system integration.

| Section | Name | Content |
|:--------|:-----|:--------|
| §0 | System Topology & Context Map | Dependency table showing how sections interconnect. Always present. |
| §1 | Current Context (Use Case Definition) | Problem/Solution boundary — what we're solving, why, and how |
| §2 | System Integration Map (Part-to-Whole) | How this agent fits into the larger system — inputs, processing, outputs, destination |

**§0 is the "wiring diagram"** — it tells the agent which sections depend on which, enabling architectural gating (if a request doesn't fit §1, it fails before reaching §3).

**§1 always follows a standard structure:**
- **Operational Mandate:** One-line declaration of what this agent does
- **The Problem:** What messy input the agent handles
- **The Solution:** How the agent solves it
- **The Mechanism:** How outputs connect to the downstream system

**§2 always follows a 4-part flow:**
1. The Inputs (Raw Data)
2. The Processing Logic (This Notebook)
3. The Output (Bridge Artifacts)
4. The Destination (The "Whole" the agent serves)

> **Source:** `00_Context_Kernel.md` (HomeLab), `MASTER_CONTEXT_HomeLab.md`, `MASTER_CONTEXT_Youtube.md`

#### MODULE 01: Logic Engine

**Purpose:** Defines the agent's transformation logic and output routing.

| Section | Name | Content |
|:--------|:-----|:--------|
| §3 | Processing Logic (Transformation Engine) | Phased processing sequence the agent executes on inputs |
| §4 | Output Routing Protocol | Where outputs go and what format they take |

**§3 always follows a phased structure:**
- **Phase A:** Filtration / Selection (what to keep, what to discard)
- **Phase B:** Entity Extraction & Schema Mapping (map inputs to target schemas)
- **Phase C:** Data Formatting (produce the final artifacts)

**§4 declares constraints:**
- What downstream system receives the output
- What format the output must take
- A pointer to §5 for exact template syntax

> **Source:** `01_Logic_Engine.md` (HomeLab), `MASTER_CONTEXT_Youtube.md` §3–§4

#### MODULE 02: Immutable Templates

**Purpose:** Defines the exact output formats the agent must produce. These are rigid schemas — the agent must not alter key names.

| Section | Name | Content |
|:--------|:-----|:--------|
| §5 | Schema Templates (Immutable) | Code-block templates with exact field names and structure |

Each template includes:
- **Source reference** — Which downstream system schema it targets
- **Purpose statement** — When to use this template
- **Code block** — The exact text pattern (key:value format, CSV, JSON, etc.)

**The "Immutable" label is critical:** These templates represent a contract with the downstream system (e.g., Notion). If the template changes, the downstream system may fail to parse the output.

> **Source:** `02_Immutable_Templates.md` (HomeLab), `MASTER_CONTEXT_Youtube.md` §5

#### MODULE 03: Reference Appendices

**Purpose:** Contains authoritative source documentation that grounds the agent's reasoning in external truth.

Content varies entirely by agent domain. Examples:

| Agent | Appendix Content |
|:------|:-----------------|
| HomeLab | Appendix A: Input Console (Home Lab Control Panel) — full Notion page structure. Appendix B: Notion's Space Explanation — Notion AI's own description of its schemas. |
| Youtube | Appendix A: Transcript Reference — pointer to the source conversation transcript. |

**The appendices are the agent's "ground truth."** When the agent extracts entities (§3) and formats output (§5), it validates against these reference documents.

> **Source:** `03_Reference_Appendices.md` (HomeLab), `MASTER_CONTEXT_Youtube.md` Module 03

### 3.3 Module Dependencies

```
MODULE 00 (Context Kernel)
    │
    │ §1 sets the problem scope
    │ §2 maps the system context
    │
    ▼
MODULE 01 (Logic Engine)
    │
    │ §3 defines processing phases
    │ §4 routes output to targets
    │
    ▼
MODULE 02 (Immutable Templates)
    │
    │ §5 provides exact output schemas
    │
    ▼
MODULE 03 (Reference Appendices)
    │
    │ Grounds all reasoning in source truth
    │
    (No downstream — terminal module)
```

---

## 4. The System_Kernel Directory

### 4.1 Purpose

In the Era 2 (Notion) implementation, each agent's MASTER_CONTEXT is backed by a `System_Kernel/` directory containing four modular source files. These files are the "source code" that compiles into the single `MASTER_CONTEXT_[AgentName].md` file.

### 4.2 File-to-Module Mapping

| File | Module | Sections Contained |
|:-----|:-------|:-------------------|
| `00_Context_Kernel.md` | MODULE 00: Context Kernel | §0 System Topology, §1 Current Context, §2 System Integration Map |
| `01_Logic_Engine.md` | MODULE 01: Logic Engine | §3 Processing Logic, §4 Output Routing Protocol |
| `02_Immutable_Templates.md` | MODULE 02: Immutable Templates | §5 Schema Templates |
| `03_Reference_Appendices.md` | MODULE 03: Reference Appendices | Appendix A, B, etc. |

### 4.3 Compilation Process

The compiled MASTER_CONTEXT is produced by **concatenating** the four module files in order (00 → 01 → 02 → 03) with module separator comments:

```markdown
# SCENARIO CONFIGURATION: [Agent Name]
> System Link: This document serves as the [MASTER_CONTEXT] for the Notion Bridge Architect.
> Operational Mode: Runtime (App Loaded)

# --------------------------------------------------------------------------------
# MODULE 00: Context Kernel
# --------------------------------------------------------------------------------

[Contents of 00_Context_Kernel.md]

# --------------------------------------------------------------------------------
# MODULE 01: Logic Engine
# --------------------------------------------------------------------------------

[Contents of 01_Logic_Engine.md]

# --------------------------------------------------------------------------------
# MODULE 02: Immutable Templates
# --------------------------------------------------------------------------------

[Contents of 02_Immutable_Templates.md]

# --------------------------------------------------------------------------------
# MODULE 03: Reference Appendices
# --------------------------------------------------------------------------------

[Contents of 03_Reference_Appendices.md]
```

The MASTER_CONTEXT header (SCENARIO CONFIGURATION + System Link + Operational Mode) is added during compilation. This header is what the Engine Core's §3 (Scenario Interface) detects to mount the cartridge.

> **GAP:** The compilation process is documented by example (comparing the HomeLab modules to the compiled `MASTER_CONTEXT_HomeLab.md`), but there is no formal compilation script or specification. The process is currently manual — an operator concatenates the files.

> **Source:** `Agent_Examples.md` §2.1–§2.2, `MASTER_CONTEXT_HomeLab.md` (compiled output vs. `System_Kernel/` source files)

### 4.4 Directory Structure

```
[Agent_Name]/
├── MASTER_CONTEXT_[Name].md          ← Compiled cartridge (paste into context window)
├── System_Kernel/                    ← Modular source files
│   ├── 00_Context_Kernel.md          (§0, §1, §2)
│   ├── 01_Logic_Engine.md            (§3, §4)
│   ├── 02_Immutable_Templates.md     (§5)
│   └── 03_Reference_Appendices.md    (Appendices)
└── Original_Source/                  ← Raw input data (transcripts, docs)
```

> **Source:** `projectNotes.md` §2 (Directory Structure), `ML_OS_DEFINITION.md` (File Structure in Practice)

---

## 5. Worked Examples

### 5.1 Side-by-Side Comparison: HomeLab vs. Youtube

The following comparison proves the pattern: two completely different domains, identical architectural structure, same Engine Core.

#### What Stays Constant

| Element | HomeLab | Youtube | Same? |
|:--------|:--------|:--------|:------|
| MASTER_CONTEXT header | `> System Link: This document serves as the [MASTER_CONTEXT]...` | `> System Link: This document serves as the [MASTER_CONTEXT]...` | Identical |
| §0 Topology table structure | 5-column table (Section ID, Component, Meta-Purpose, Dependencies) | Identical 5-column table | Identical |
| §0 Topology content | §1→§3, §2→§4, §3→§4, §4→§5 | §1→§3, §2→§4, §3→§4, §4→§5 | Identical |
| §0 System Instruction | "You must treat these sections as interconnected modules..." | Identical instruction | Identical |
| Module separator comments | `# MODULE 00: Context Kernel` etc. | Identical separators | Identical |
| §3 Phase structure | Phase A → Phase B → Phase C | Phase A → Phase B → Phase C | Identical pattern |
| §4 constraint pattern | "All Direct Input artifacts must strictly match the syntax defined in §5" | Same constraint pattern | Identical |
| §5 header | "Meta-Purpose: These are the exact text patterns required by..." | Same meta-purpose pattern | Identical |

#### What Changes

| Element | HomeLab | Youtube |
|:--------|:--------|:--------|
| **§1 Operational Mandate** | "Home Lab Control Center Bridge" | "Youtube Content Extraction & Architecture" |
| **§1 The Problem** | Lab ops generate messy transcripts | Creative brainstorming generates messy transcripts |
| **§1 The Solution** | Logic filter between "The Plan" and "The Reality" | Logic filter between "The Brainstorm" and "The Content Calendar" |
| **§2 Inputs** | The Plan + The Reality (transcript) | The Transcript + The Goal |
| **§2 Destination** | Notion databases (Node Inventory, VLANs, Config Snapshots) | Youtube Notion Space (to-be-built) |
| **§3 Phase A** | Noise Filtration ("Final State" Check) | Cognitive Filtration (Idea Crystallization) |
| **§3 Phase B** | Entity Extraction → Nodes, VLANs, Snapshots | Entity Extraction → Video Concepts, Assets, Strategies |
| **§3 Phase C** | Sanitized Narrative + Structured Payload | Project Overview + Structured Payload |
| **§4 Output targets** | 'Change Narratives' + 'Node Direct Inputs' | 'Project Architecture Strategy' + 'Video Direct Inputs' |
| **§5 Templates** | Node Direct Input, VLAN Direct Input (with exact field schemas) | Video Direct Input, Strategy Direct Input (proposed schemas) |
| **Module 03 Appendices** | Full Notion page documentation (Input Console, Notion's Space Explanation, 260+ lines) | Transcript reference pointer (minimal) |

#### The Proof

The HomeLab agent processes **infrastructure transcripts → Notion database updates**.
The Youtube agent processes **brainstorming transcripts → content pipeline entries**.

Both agents:
1. Load the **same Engine Core** (`NotionBridgeArchitect.md`)
2. Follow the **same §0 topology**
3. Execute the **same 3-phase processing pattern** (Filter → Extract → Format)
4. Route output through the **same §4 → §5 enforcement chain**

The *only* differences are domain-specific: what data they extract, what schemas they target, and what reference documentation they consult.

> **Source:** `MASTER_CONTEXT_HomeLab.md`, `MASTER_CONTEXT_Youtube.md`

### 5.2 Third Example: Cursor Context Synthesis Agent

A third MASTER_CONTEXT exists in `AGENT_SCENARIO_Synthesis.md`. It follows the same pattern but with a simplified topology (§1 → §3 → §5, no §2 or §4) because it doesn't route output to an external system like Notion AI.

This demonstrates that the pattern is flexible: modules can be omitted when they serve no purpose for a given agent's mission.

> **Source:** `AGENT_SCENARIO_Synthesis.md`

---

## 6. The Seed Chat Protocol

### 6.1 Definition

The Seed Chat Protocol is a mechanism to inject **"Synthetic History"** or **"Frozen Epistemic State"** into a new agent, enabling knowledge continuity without context bloat.

Also referred to as **"Timeline Stitching"** or **"Multi-Dimensional Prompting."**

### 6.2 Mechanism

| Step | Action | Detail |
|:-----|:-------|:-------|
| 1 | **Capture** | A "Seed Chat" file is created by copying a critical conversation state — the moment where key knowledge was established. |
| 2 | **Storage** | Saved as `System_Kernel/04_Seed_Chat.md` — a fifth module in the System_Kernel directory. |
| 3 | **Injection** | The Bootloader (`MASTER_CONTEXT.md`) ingests this file, instructing the agent to "Treat this text as your own memory of previous events." |

### 6.3 Result

The agent wakes up "already up to speed" — it has the knowledge from a previous session without carrying the full conversation history. This enables:

- **Knowledge continuity** between sessions
- **Context efficiency** — only the critical epistemic state is preserved, not the full transcript
- **Timeline stitching** — the new agent's memory begins from a deliberately chosen point

### 6.4 Implementation Status

| Aspect | Status |
|:-------|:-------|
| Concept | Documented in `Kernel_App_Definition.md` §5 |
| File location | `System_Kernel/04_Seed_Chat.md` (specified) |
| Working implementation | **None.** No agent currently uses a 04_Seed_Chat.md file. The protocol is design-only. |
| Bootloader integration | **Not implemented.** The Engine Core does not currently reference or load 04_Seed_Chat.md. |

> **Source:** `Kernel_App_Definition.md` §5 (The Seed Chat Protocol)

---

## 7. Cursor Translation Notes

This section maps each ML OS component to its Cursor IDE equivalent. These are **annotations**, not decisions — the translation is in progress and many questions remain open.

### 7.1 Mapping Table

| ML OS Component | NotebookLM/Notion Implementation | Cursor Equivalent | Confidence | Notes |
|:----------------|:---------------------------------|:-------------------|:-----------|:------|
| **Engine Core** | Single `.md` file pasted into context window | `alwaysApply: true` rule(s) in `.cursor/rules/` OR a Python bootloader that computes the system prompt | Medium | `alwaysApply` injects into every prompt — mirrors the Engine Core's universal presence. But Cursor's context budget may not tolerate a full Engine Core as an always-on rule. A Python bootloader could dynamically generate a minimal kernel. |
| **MASTER_CONTEXT** | Single `.md` file pasted alongside Engine Core | Sprint-specific `.mdc` rules activated via `globs` or `description` triggers, plus `PROBLEM.md` as the state/RAM | Medium | In Cursor, context is computed, not pasted. Sprint folder structure + `.mdc` rules replace the monolithic MASTER_CONTEXT. |
| **System_Kernel/ modules** | Four `.md` files (00–03) compiled into MASTER_CONTEXT | `.cursor/rules/` hierarchy with purpose-specific rules | Medium | Each module maps to one or more `.mdc` files. The compilation step disappears — Cursor injects rules on-demand. |
| **§0 System Topology** | Markdown table at top of MASTER_CONTEXT | Rule dependency management — possibly `description` fields that reference other rules, or a `00_index.mdc` that declares the dependency graph | Low | Cursor has no native concept of rule dependencies. This may need custom tooling. |
| **§1 Current Context** | Problem/Solution boundary in MASTER_CONTEXT | `PROBLEM.md` in the sprint folder — already used as the "App Data" / "RAM" | High | Direct mapping. `PROBLEM.md` already serves this role in current Cursor sprints. |
| **§3 Processing Logic** | Phased transformation sequence | Agent instructions embedded in task-specific rules or custom modes | Medium | Could be a `description`-triggered rule that activates when the user expresses processing intent. |
| **§5 Immutable Templates** | Code blocks with exact output schemas | Template rules with `globs` targeting output files, or Notepads with schema references | Medium | Templates need to be available but not always injected — `globs` or `description` triggers are appropriate. |
| **Module 03 Appendices** | Reference documentation embedded in MASTER_CONTEXT | Cursor `@Docs` references, or files in the workspace accessible via `@file` | High | Cursor's `@Docs` RAG system is purpose-built for this. External documentation can be indexed once and retrieved on demand. |
| **Bootloader (§1.4)** | Manual paste of Engine Core into context window | Python bootloader script that computes system state at session start | Medium | A Python bootloader could read workspace state, check for `PROBLEM.md`, verify sprint context, and generate a dynamic system prompt. This shifts ML OS from "rulebook" to "runtime." |
| **Runtime Grounding (§1.7)** | Agent executes 5-step verification sequence on command | A bootloader function OR an `alwaysApply` rule that auto-grounds | Medium | Could be triggered by a custom slash command or run automatically at session start. |
| **Seed Chat (§5 of KAD)** | `04_Seed_Chat.md` ingested by Bootloader | `.specstory/history/` transcript references via `@` mentions | High | Cursor's `.specstory` folder already captures conversation history. A curated transcript could serve the same purpose as a Seed Chat. |
| **Variable binding** | Declared in §1.4, bound at boot | Cursor environment variables, or computed values injected by a Python bootloader | Low | Cursor has no native variable binding for `.mdc` rules. A bootloader would need to template-substitute variables into rules. |

> **Source:** `00_INDEX.md` (mapping table), `06_ConditionalRuleDesign.md` (activation triggers)

### 7.2 Cursor Rule Activation Patterns

Cursor `.mdc` rules use three activation triggers, each mapping to a different ML OS concept:

| Trigger | Syntax | ML OS Equivalent | Best For |
|:--------|:-------|:------------------|:---------|
| `alwaysApply: true` | `alwaysApply: true` | Engine Core (§1, §2) — always present | Core identity, reasoning protocol, output format |
| `globs` | `globs: ["src/**/*.ts"]` | System_Kernel modules — activated by file context | Technology-specific standards, template enforcement |
| `description` | `description: "Use when user asks about..."` | Scenario Interface (§3) — activated by intent | Topic-based or workflow-based guidance |

**The Compound Gate pattern** (from `06_ConditionalRuleDesign.md`) combines `globs` + `description` to create conditional activation: the rule only fires when the user is in a specific file context AND expressing a specific intent. This maps to the MASTER_CONTEXT's architectural gating (§0 → §1 → §3 scope control).

> **Source:** `06_ConditionalRuleDesign.md` §1–§4

### 7.3 Key Insight: Rulebook to Runtime

The fundamental shift in the Cursor port is:

| Aspect | NotebookLM/Notion | Cursor |
|:-------|:-------------------|:-------|
| Context delivery | Manual paste (static) | Automatic injection (dynamic) |
| Prompt construction | Written input (operator assembles it) | Computed output (system builds it) |
| Tool access | None (text-only) | Full (Python scripts, MCP, terminal) |
| State persistence | None between sessions | `.specstory/history/`, memories, rules |
| Context budget | Large (NotebookLM) | Constrained (Cursor token limits) |

A Python bootloader can **COMPUTE** system prompts from live workspace state — reading `PROBLEM.md`, checking sprint folder structure, discovering available tools — rather than relying on a static markdown file pasted into a context window.

> **Source:** `00_INDEX.md` §"How This Relates to CursorMLOSDev", `projectNotes.md` §6

---

## 8. Open Questions

These architectural decisions remain unmade for the Cursor port:

### 8.1 Engine Core Translation

1. **Should the Engine Core be a single `alwaysApply` rule or multiple rules?** A single rule preserves the monolithic identity but may consume too much context budget. Multiple rules allow selective loading but fragment the kernel.

2. **Should the Engine Core be static (`.mdc`) or dynamic (Python bootloader)?** Static is simpler and transparent. Dynamic enables computed context but adds complexity and a Python dependency.

3. **How do you handle the immutability contract in Cursor?** `.mdc` rules can be edited at any time — there is no enforcement mechanism analogous to "§1 cannot be overridden." Should the bootloader validate rule integrity via checksums?

### 8.2 MASTER_CONTEXT Translation

4. **Does `PROBLEM.md` fully replace §1 (Current Context)?** It currently serves as state/RAM but doesn't follow the Problem/Solution/Mechanism structure. Should it be standardized?

5. **How are Modules 01–03 represented?** As individual `.mdc` rules? As files in the sprint folder? As computed context injected by a bootloader?

6. **How is the §0 System Topology represented?** Cursor has no native rule dependency system. Options: (a) a `00_index.mdc` that lists dependencies, (b) `description` fields that cross-reference other rules, (c) a Python dependency resolver.

### 8.3 Runtime Protocols

7. **How is the Runtime Grounding Sequence triggered in Cursor?** Options: (a) a custom slash command, (b) an `alwaysApply` rule that runs a grounding check, (c) a Python bootloader invoked at session start, (d) a `.specstory` transcript that includes a grounding prompt.

8. **How does the Seed Chat Protocol translate?** `.specstory/history/` captures full transcripts, but the Seed Chat concept requires *curated* excerpts. Is there a mechanism to mark critical conversation states for future injection?

### 8.4 Variable System

9. **How are ML OS variables (`$AGENT_NAME`, etc.) bound in Cursor?** Cursor rules are static text — there is no variable substitution. Options: (a) a Python bootloader that templates variables into rules, (b) Cursor environment variables (if they exist), (c) abandon formal variables and use natural language instead.

10. **Does the variable system even matter in Cursor?** In NotebookLM, variables provided formal governance. In Cursor, the agent's identity comes from rules + workspace context + conversation history. The governance model may need to be rethought rather than directly ported.

### 8.5 Compilation & Distribution

11. **Is the MASTER_CONTEXT compilation step still needed?** In NotebookLM, you need a single pasted file. In Cursor, rules are injected individually. The compilation step may become unnecessary — or it may be replaced by a "context pack" that bundles rules + PROBLEM.md + reference docs.

12. **How are agents distributed?** In Era 2, you copy a folder. In Cursor, should an agent be a `.cursor/rules/` hierarchy? A git-clonable template? A Python package?

---

## Appendix A: File Reference

### Engine Core

| File | Path | Purpose |
|:-----|:-----|:--------|
| NotionBridgeArchitect.md | `Notion_Agents/_Engine_Core/NotionBridgeArchitect.md` | The Engine Core (§1–§3) |

### Working MASTER_CONTEXT Implementations

| Agent | Compiled Cartridge | System_Kernel/ |
|:------|:-------------------|:---------------|
| HomeLab Transcript Connector | `Notion_Agents/HomeLab_Transcript_Connector/MASTER_CONTEXT_HomeLab.md` | `System_Kernel/00-03` |
| Youtube Agent | `Notion_Agents/Youtube_Agent/MASTER_CONTEXT_Youtube.md` | (no separate kernel files) |
| Cursor Context Synthesis | `CursorMLOSDev/research/cursor-context/AGENT_SCENARIO_Synthesis.md` | (standalone) |

### Architecture Documentation

| File | Path | Content |
|:-----|:-----|:--------|
| Project Notes | `Notion_Agents/projectNotes.md` | Platform vs. App concept |
| Kernel/App Definition | `Sprint_Meta/.../Kernel_App_Definition.md` | Formal spec + Seed Chat |
| Agent Examples | `Sprint_Meta/.../Agent_Examples.md` | Fractal Kernel Standard v2.0 |
| ML OS Definition | `Sprint_ML_OS_Architect/.../ML_OS_DEFINITION.md` | Best prior consolidation |
| §1-S Spec | `Sprint_ML_OS_Architect/.../Supplemental_System_Documentation.md` | Extensible reference layer |

### Cursor Research

| File | Path | Content |
|:-----|:-----|:--------|
| Research Index | `CursorMLOSDev/research/cursor-context/00_INDEX.md` | ML OS → Cursor mapping |
| Conditional Rules | `CursorMLOSDev/research/cursor-context/06_ConditionalRuleDesign.md` | Activation triggers |

---

*Generated by ML OS Consolidation Architect | 2026-02-06 | $OUTPUT_FORMAT = MARKDOWN_RAW*
