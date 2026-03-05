# The Verb Cipher Protocol

> A cognitive depth filter for the CompTIA Network+ (N10-009) exam, validated against CompTIA's own instructional design framework.

---

## Core Philosophy

**We do not study "topics." We study "cognitive requirements."**

CompTIA designs exam questions using Bloom's Taxonomy — the same framework taught in their Certified Technical Trainer (CTT+) program. The **command verb** in each exam objective encodes exactly how deep the exam will test that topic.

- If CompTIA asks for **Knowledge** → Build **Flashcards**
- If CompTIA asks for **Application** → Build **Labs**
- If CompTIA asks for **Analysis** → Build **Troubleshooting Scenarios**

---

## The Decoder Ring

### Source of Truth
- **Primary Reference:** CompTIA N10-009 Official Exam Objectives (Appendix A)
- **Validation Reference:** CompTIA CTT+ Bloom's Taxonomy cognitive domain definitions

We determine the required depth for every objective by mapping its **command verb** to the corresponding **cognitive domain**.

---

### Level 1: KNOWLEDGE (Flashcard Tier)

**Goal:** Recall and Comprehension.

**Trigger Verbs:** Explain, Summarize, Compare, Contrast, Identify, Define, Label, List.

**CTT+ Definition:** *"A component of the cognitive domain in Bloom's Taxonomy. This element is evident when a person can recall specific information, technical terms, and concepts, and answer questions about the technology."*

**Study Action:**
- Create flashcards (definition/concept)
- **Strict Prohibition:** DO NOT build a lab for Level 1 objectives

**Example:**
- Objective 1.1: "**Explain** concepts related to the OSI reference model"
- Action: Flashcards for each layer. Do NOT build a "lab to explain the OSI model."

---

### Level 2: APPLICATION (Configuration Lab Tier)

**Goal:** Mechanism and proficiency.

**Trigger Verbs:** Configure, Implement, Deploy, Demonstrate, Operate, Use, Apply.

**CTT+ Definition:** *"Application of knowledge is expressed by taking existing comprehension and applying it to new scenarios and problems."*

**Study Action:**
- Configuration labs (Proxmox, pfSense, or equivalent)
- Focus on syntax, click-paths, and verification commands

**Example:**
- Objective 2.2: "Given a scenario, **configure** switching technologies and features"
- Action: Lab — configure VLANs, trunking, STP on a virtual switch. Verify with `show vlan brief`.

---

### Level 3: ANALYSIS (Troubleshoot Tier)

**Goal:** Diagnosis and root cause analysis.

**Trigger Verbs:** Troubleshoot, Analyze, Distinguish, Resolve, Differentiate.

**CTT+ Definition:** *"Analysis in the cognitive domain is demonstrated by examining a problem or scenario and thinking through its root causes and causal factors."*

**Study Action:**
- Break-Fix scenarios
- Intentionally misconfigure a working system
- Use logs and tools to diagnose and fix
- **Priority:** This level represents **24%** of the exam (Domain 5.0)

**Example:**
- Objective 5.3: "Given a scenario, **troubleshoot** common issues with network services"
- Action: Break a working DHCP server (exhaust the scope, misconfigure the gateway). Diagnose using `ipconfig /all` and Wireshark (`bootp` filter).

---

## The Extraction Workflows

### Workflow A: The "Trap Lab" Filter

**Purpose:** Strip unnecessary busy-work from textbook lab assignments.

**Decision Logic:**
1. Identify the textbook's lab topic
2. Cross-reference against the official objective's command verb
3. If the textbook assigns a lab BUT the objective verb is "Explain" or "Summarize" → **TRAP** (read only, do not build)
4. If the textbook assigns a lab AND the objective verb is "Configure" / "Troubleshoot" → **APPROVED** (build it)

**Example:** A textbook may assign a "lab" to "set up a wiki for documentation" for Objective 3.1. But CompTIA only asks to "**Explain** organizational processes and documentation." The wiki lab is a trap — it consumes hours for zero exam points.

### Workflow B: The "Void" Check

**Purpose:** Find where the textbook fails to provide necessary depth.

**Decision Logic:**
1. Scan the exam objectives for "Troubleshoot" or "Given a scenario..."
2. Verify: Does the textbook have a specific lab for this?
3. If Missing → **GAP DETECTED** — generate a custom lab

**Example:** CompTIA requires troubleshooting cable faults (TDR readings, split pairs, crosstalk). If the textbook only teaches cable *making* (crimping RJ-45 connectors), that is a gap. A custom break-fix lab must be created.

### Workflow C: The Acronym Scrub

**Purpose:** Prevent memorizing legacy or dead technology.

**Decision Logic:**
1. Collect the textbook's "Key Terms" per chapter
2. Filter against the official N10-009 acronym list (last pages of Appendix A)
3. If a term is NOT on the official list → Discard it

---

## The N10-009 Objective Classification

| Obj ID | Objective | Command Verb | Level |
|--------|-----------|-------------|-------|
| 1.1 | OSI Reference Model | Explain | L1 |
| 1.2 | Networking Appliances, Devices, Functions | Compare | L1 |
| 1.3 | Cloud Concepts and Connectivity | Summarize | L1 |
| 1.4 | Ports, Protocols, Services, Traffic Types | Explain | L1 |
| 1.5 | Transmission Media and Cabling | Compare | L1 |
| 1.6 | Topologies, Architectures, Types | Compare | L1 |
| 1.7 | IPv4 Network Addressing | Use | **L2** |
| 1.8 | Modern Network Environments | Summarize | L1 |
| 2.1 | Routing Technologies | Explain | L1 |
| 2.2 | Switching Technologies and Features | Configure | **L2** |
| 2.3 | Wireless Devices and Technologies | Configure | **L2** |
| 2.4 | Physical Installations | Explain | L1 |
| 3.1 | Organizational Processes and Documentation | Explain | L1 |
| 3.2 | Network Monitoring Technologies | Use | **L2** |
| 3.3 | Disaster Recovery Concepts | Explain | L1 |
| 3.4 | IPv4 and IPv6 Network Services | Implement | **L2** |
| 3.5 | Network Access and Management Methods | Compare | L1 |
| 4.1 | Basic Network Security Concepts | Explain | L1 |
| 4.2 | Types of Attacks and Impact | Summarize | L1 |
| 4.3 | Network Security Features and Solutions | Apply | **L2** |
| 5.1 | Troubleshooting Methodology | Explain | L1 |
| 5.2 | Cabling and Physical Interface Issues | Troubleshoot | **L3** |
| 5.3 | Network Services Issues | Troubleshoot | **L3** |
| 5.4 | Performance and Connectivity Issues | Troubleshoot | **L3** |
| 5.5 | Appropriate Tool or Protocol | Use | **L2** |

### Distribution

| Level | Count | Percentage | Study Action |
|-------|-------|-----------|-------------|
| Level 1 (Knowledge) | 15 | 60% | Flashcards only |
| Level 2 (Application) | 7 | 28% | Configuration labs |
| Level 3 (Analysis) | 3 | 12% | Break-Fix scenarios |

**Key Insight:** 60% of objectives require only flashcards. The exam's real difficulty is concentrated in the 40% that require hands-on competence — and especially the three Level 3 objectives that constitute Domain 5's 24% exam weight.
