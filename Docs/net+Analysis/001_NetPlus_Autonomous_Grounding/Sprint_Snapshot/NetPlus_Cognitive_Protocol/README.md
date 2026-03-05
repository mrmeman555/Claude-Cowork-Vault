# NetPlus-Cognitive-Protocol

> A Systems Engineering approach to reverse-engineering the CompTIA Network+ (N10-009) exam.

## What This Is

This is not a study guide. This is the **source code** for a cognitive framework that decomposes the Network+ exam into a structured, queryable system.

Instead of memorizing 25 objectives linearly, this framework maps every exam topic to a **three-dimensional coordinate system** that reveals hidden dependencies, eliminates wasted study time, and concentrates effort where the exam actually tests.

## The Core Architecture

### 1. The Verb Cipher Protocol

CompTIA designs exam questions using [Bloom's Taxonomy](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy) — the same framework used in their Certified Technical Trainer (CTT+) program. The **command verb** in each exam objective encodes exactly how deep the exam will test.

| Level | Verbs | What CompTIA Expects | Study Action |
|-------|-------|---------------------|-------------|
| **Knowledge** | Explain, Compare, Summarize, Identify | Recall and comprehension | Flashcards only. Do NOT build a lab. |
| **Application** | Configure, Implement, Use, Apply | Operational competence | Configuration labs. Know the syntax. |
| **Analysis** | Troubleshoot, Analyze, Resolve | Diagnosis and root cause | Break-Fix scenarios. Intentionally break a working system and fix it. |

This eliminates ~60% of busy-work labs that textbooks assign for topics the exam only tests at "Explain" depth.

See: [`01_The_Verb_Cipher/`](01_The_Verb_Cipher/)

### 2. The Three Trees of Troubleshooting

Domain 5.0 (Network Troubleshooting) is 24% of the exam — the largest domain. It is not a list of topics. It is **three distinct failure-mode trees** that all other domains feed into:

| Tree | Objective | Failure Domain | Question It Answers |
|------|-----------|---------------|-------------------|
| **Physical** (PHY) | 5.2 | Hardware, Cables, Power | Is the thing broken, dead, or miswired? |
| **Logical** (LOG) | 5.3 | Protocols, Addresses, Services | Is the config wrong, the address wrong, the service down? |
| **Performance** (PRF) | 5.4 | Flow, Capacity, Latency | Does the thing work but is it slow, congested, or dropping packets? |

See: [`02_The_Dependency_Map/`](02_The_Dependency_Map/)

### 3. The 3D Coordinate Schema

Every exam objective can be mapped to three coordinates:

- **Lens (Vertical):** Which failure-mode tree does it feed? `[PHY]`, `[LOG]`, or `[PRF]`
- **Tool (Horizontal):** Which diagnostic instrument (Obj 5.5) inspects it?
- **Method (Depth):** Which stage of the troubleshooting methodology (Obj 5.1) applies?

This transforms the flat objective list into a structured database. When studying VLANs, you don't just "learn VLANs." You learn:
- **Lens:** `[LOG]` — the failure mode is a mismatched native VLAN
- **Tool:** `show vlan brief` / Wireshark
- **Method:** "Test the Theory" — if ping fails, is the 802.1Q tag missing?

See: [`03_The_Matrices/`](03_The_Matrices/)

### 4. The Dependency DAG

Level 2 (Application) skills are "locked" behind Level 1 (Knowledge) prerequisites. Level 3 (Analysis) skills require Level 2 mastery. This creates a directed acyclic graph that determines optimal study order.

**Critical finding:** Objective 1.4 (Ports, Protocols, Services) is the single most connected knowledge node — it feeds 9 of the 25 objectives. Master this first.

See: [`02_The_Dependency_Map/`](02_The_Dependency_Map/)

## Methodology

This framework was designed using:
- **CompTIA N10-009 Official Exam Objectives** (freely available at [comptia.org](https://www.comptia.org/certifications/network))
- **Bloom's Taxonomy** cognitive depth framework (as used in CompTIA CTT+ training materials)
- **Deep Research Prompts** — adversarial roundtable prompts designed to force multi-perspective analysis

No proprietary textbook content is included. All analysis is derived from the publicly available exam objectives document and open pedagogical frameworks.

## Repository Structure

```
NetPlus-Cognitive-Protocol/
├── README.md                          ← You are here
├── 01_The_Verb_Cipher/
│   └── Protocol.md                    ← The Bloom's Taxonomy filter
├── 02_The_Dependency_Map/
│   ├── Troubleshooting_Vectors.md     ← Three Trees + Dependency DAG
│   └── Skill_Trees.md                ← Mermaid.js dependency visualizations
├── 03_The_Matrices/
│   └── 3D_Mapping_Table.md            ← Full exam mapped to Lens/Tool/Method
├── 04_Tools_and_Scripts/
│   └── Deep_Research_Prompts.md       ← The prompts used to generate the analysis
└── LICENSE
```

## Who This Is For

- **Network+ candidates** who want to study smarter, not harder
- **IT professionals** interested in systematic approaches to certification prep
- **Prompt engineers** interested in using AI for structured knowledge extraction
- **Anyone** who thinks "just read the book" is an inefficient strategy

## The "Reverse-Engineering" Angle

CompTIA publishes the exam objectives. They also publish (via CTT+) the cognitive framework they use to write questions. This project connects those two public documents to derive the exam's internal architecture — revealing which topics need labs, which need flashcards, and which need break-fix scenarios.

This is not a cheat sheet. It is a systems engineering analysis of a public specification.

## License

MIT License. See [LICENSE](LICENSE).
