# Deep Research Prompts

> The actual "source code" — the adversarial prompts used to generate the analysis in this repository.

---

## Methodology: The Roundtable

These prompts use the **Architect's Roundtable** methodology: instead of asking a single question, we simulate multiple expert personas who challenge each other's assumptions before synthesizing a unified output.

This produces more rigorous, multi-perspective analysis than a standard prompt because each expert has a specific mandate to **reject** shallow answers and **demand** a specific type of rigor.

### Structure
1. **Persona** — Define 4-5 adversarial expert specialists
2. **Context** — Provide the problem specification and constraints
3. **Phase 1: Adversarial Debate** — Each expert poses probing questions
4. **Phase 2: Synthesis** — Combine constraints into structured output
5. **Output Schema** — Define the exact table/document format required

---

## Prompt 1: The 3D Objective Mapping

**Purpose:** Map all 25 N10-009 objectives to three coordinates (Lens, Tool, Method).

**Expert Panel:**
| Expert | Focus | Rejects | Demands |
|--------|-------|---------|---------|
| Bloom's Taxonomy Enforcer | Cognitive depth verification | Gut-feel difficulty ratings | Classification strictly from command verb |
| Network Failure Mode Analyst | Troubleshooting lens assignment | "This is a networking topic" | Precise identification of HOW each topic breaks |
| Toolchain Mapper | Instrument-to-objective binding | "You use various tools" | Specific tool + filter/context for each objective |
| Dependency Graph Architect | Prerequisite chain tracing | "Study in chapter order" | Explicit DAG from L1 → L2 → L3 |
| Meta-Prompt Engineer | Structure and completeness | Vague analysis, empty cells | Complete table with every cell filled |

**Key Adversarial Questions:**
- "Objective 2.3 (Wireless) is a triple-lens objective. How do we represent PHY (antenna), LOG (auth), and PRF (throughput) without losing the Lens Locking benefit?"
- "Level 1 objectives don't generate labs, but they DO have associated tools for downstream troubleshooting. How do we bind a 'conceptual tool' vs. a 'physical tool'?"
- "The existing dependency map covers 5.2/5.3/5.4 prerequisites. But I need the FULL graph — every L2 traces to L1, every L3 traces through L2 to L1."

**Output:** The Master 3D Mapping Table (see `03_The_Matrices/3D_Mapping_Table.md`).

---

## Prompt 2: Difficulty Calibration

**Purpose:** Calibrate expectations of actual exam difficulty against the candidate's study depth.

**Expert Panel:**
| Expert | Focus | Rejects | Demands |
|--------|-------|---------|---------|
| Psychometrician | Item difficulty and taxonomy | Anecdotal difficulty ratings | Analysis based on Bloom's Taxonomy |
| Content Domain Architect | Syllabus topography | Depth by default | Precise "Mile-Wide/Inch-Deep" vs. "Deep-Dive" mapping |
| Cognitive Efficiency Strategist | Study ROI | Over-learning | "Stop-Studying-When" criteria per domain |
| PBQ Game Theorist | Simulation mechanics | "Real-world equivalence" | Analysis of interface limitations and logic puzzle rules |
| Meta-Prompt Engineer | Epistemic calibration | Motivational fluff | Ground truth reality checks via data |

**Key Research Directives:**
- **Pass 1:** Syllabus Topography (breadth vs. depth per domain)
- **Pass 2:** Item Design Analysis (cognitive load and reasoning types)
- **Pass 3:** Simulation Mechanics (deconstructing Performance-Based Questions)
- **Pass 4:** Efficiency Audit (diminishing returns identification)
- **Pass 5:** Final Calibration (defining "Ready")

**Output:** Depth-O-Meters per domain, Trap Identification lists, Stop-Studying Criteria.

---

## How to Use These Prompts

### With Gemini Deep Research
1. Open a new Gemini Deep Research session
2. Paste the full prompt as the initial query
3. Attach the supporting context documents (exam objectives PDF, Verb Cipher Protocol)
4. Let the deep research engine execute

### With Other AI Tools
These prompts work with any capable AI model (Claude, GPT-4, etc.). The Roundtable structure forces rigorous analysis regardless of the model. For best results:
- Provide the full prompt without truncation
- Attach all referenced context documents
- Request the output in the exact format specified

### Adapting for Other Certifications
The Roundtable methodology is certification-agnostic. To adapt for Security+, CCNA, or any other exam:
1. Replace the objective list with the target exam's objectives
2. Adjust the Verb Cipher verbs if the certification body uses different terminology
3. Modify the "Three Trees" to match the target exam's troubleshooting taxonomy
4. Keep the expert panel structure — adversarial debate produces better analysis than cooperative agreement
