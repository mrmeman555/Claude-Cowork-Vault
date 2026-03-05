# 01 Protocol: The Verb Cipher (Depth Analysis Methodology)

## 1. Core Philosophy
**Objective:** Maximize exam ROI by aligning study depth strictly with CompTIA's internal design standards (Bloom's Taxonomy).
**The Rule:** We do not study "topics." We study "cognitive requirements."
- If CompTIA asks for **Knowledge**, we build **Flashcards**.
- If CompTIA asks for **Application**, we build **Labs**.
- If CompTIA asks for **Analysis**, we build **Troubleshooting Scenarios**.

## 2. The Source of Truth (The Decoder Ring)
**Primary Reference:** `Appendix_A_Exam_Objectives.pdf` (Official N10-009)
**Validation Reference:** `CTT_Reference_Materials.pdf` (CompTIA Certified Technical Trainer Guide, Table 8-1)

We determine the required depth for every objective by mapping its **Command Verb** to the **CTT+ Cognitive Domain**.

### 🟢 Level 1: KNOWLEDGE (Flashcard Tier)
* **Goal:** Recall and Comprehension.
* **Trigger Verbs:** *Explain, Summarize, Compare, Contrast, Identify, Define, Label, List.*
* **Action:**
    * Create Anki Card (Definition/Concept).
    * **Strict Prohibition:** DO NOT build a lab. (e.g., Do not build a lab to "Explain" MPLS. Just know what it is.)

### 🟡 Level 2: APPLICATION (Config Lab Tier)
* **Goal:** Mechanism and proficiency.
* **Trigger Verbs:** *Configure, Implement, Deploy, Demonstrate, Operate, Use, Apply.*
* **Action:**
    * **Lab Requirement:** Must be executed in Proxmox/pfSense.
    * **Focus:** Syntax, click-paths, and verification commands.

### 🔴 Level 3: ANALYSIS (Troubleshoot Tier)
* **Goal:** Diagnosis and root cause analysis.
* **Trigger Verbs:** *Troubleshoot, Analyze, Distinguish, Resolve, Differentiate.*
* **Action:**
    * **Break-Fix Scenario:** Intentionally misconfigure a working system and use logs/tools to fix it.
    * **Priority:** This is **24%** of the exam (Domain 5.0).

---

## 3. The Extraction Workflows

### Workflow A: The "Trap Lab" Filter
**Purpose:** To strip unnecessary busy-work from the Cengage textbook.
1.  **Ingest:** Cengage "Hands-On Projects" list for the Chapter.
2.  **Cross-Reference:** Check the topic against the Official Objective Verb.
3.  **Decision Logic:**
    * If Cengage = "Lab" AND CompTIA = "Configure/Troubleshoot" → **✅ APPROVED (Build it).**
    * If Cengage = "Lab" BUT CompTIA = "Explain" → **⛔ TRAP (Read only, do not build).**

### Workflow B: The "Void" Check
**Purpose:** To find where the textbook fails to provide necessary depth.
1.  **Scan:** CompTIA Objectives for "Troubleshoot" or "Given a scenario..."
2.  **Verify:** Does Cengage have a specific lab for this?
3.  **Decision Logic:**
    * If Missing → **⚠️ GAP DETECTED.** (Generate custom Proxmox scenario using `net+ agent`).

### Workflow C: The Acronym Scrub
**Purpose:** To prevent memorizing legacy/dead technology.
1.  **Ingest:** Cengage "Key Terms" list.
2.  **Filter:** Compare against `Appendix_A` Acronym List (last pages).
3.  **Action:** If not on the official list, discard.

---

## 4. Execution Prompts
*Use these prompts in Cursor to execute this protocol.*

**To Analyze a Chapter:**
> "Apply the Verb Cipher Protocol to [Chapter X]. Cross-reference the 'Hands-On Projects' against the Official N10-009 Objectives. Output a table of 'Approved Labs' vs 'Trap Labs' based on the verb depth."

**To Generate a Lab:**
> "Generate a Level 3 Break-Fix Scenario for [Objective 5.2] using my Proxmox/pfSense stack. The objective verb is 'Troubleshoot', so focus on log analysis and isolation."
