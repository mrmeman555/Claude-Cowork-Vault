# Brainstorming: Objective Architecture & Dependency Logic

> **Purpose:** To analyze the "Pedagogical Architecture" of the exam. This file maps the hidden relationships and dependencies between objectives, moving beyond simple lists to a "Skill Tree."

## 🏗️ The Domain Logic (The Holistic Story)
CompTIA N10-009 is not a random list of facts. It is a linear narrative of a Network Engineer's lifecycle.

| Domain | Weight | The "Meta-Task" | Cognitive Role |
|---|---|---|---|
| **1.0 Concepts** | 23% | **The Dictionary** | **Foundation.** You cannot speak the language without this. Mostly Level 1 (Knowledge). |
| **2.0 Implementation** | 20% | **The Build** | **Creation.** Using the Dictionary to build infrastructure. Heavy Level 2 (Application). |
| **3.0 Operations** | 19% | **The Run** | **Maintenance.** Keeping the build alive. Policy, Monitoring, DR. |
| **4.0 Security** | 14% | **The Protect** | **Hardening.** Securing the build and operations. |
| **5.0 Troubleshooting** | 24% | **The Fix** | **Mastery.** You cannot fix what you do not understand (D1) or know how to build (D2). Heavy Level 3 (Analysis). |

## 🌳 The Skill Tree (Dependency Mapping)
*Hypothesis: Level 2/3 Skills are "locked" behind Level 1 Knowledge Nodes.*

### Example: The "Switching" Skill Tree
**Target Skill:** Configure Switching (Objective 2.2 - Level 2)
*   **Dependency A:** Knowledge of Hardware (Objective 1.2 - Level 1) -> *Must know what a switch IS.*
*   **Dependency B:** Knowledge of Topologies (Objective 1.6 - Level 1) -> *Must know WHERE it fits.*
*   **Dependency C:** Knowledge of Ports/Protocols (Objective 1.4 - Level 1) -> *Must know HOW it talks.*

**Target Skill:** Troubleshoot Switching (Objective 5.3 - Level 3)
*   **Dependency:** Mastery of Objective 2.2 (Configuration).
*   **Logic:** You cannot detect a "misconfiguration" (Troubleshooting) if you do not know the "correct configuration" (Implementation).

## 🧭 Study Implication
We should **Serialize** the study plan based on these dependencies, not just Chapter order.
*   *Rule:* Do not attempt a Lab (Level 2) until the Prerequisite Flashcards (Level 1) are mastered.
*   *Rule:* Do not attempt a Break-Fix (Level 3) until the Configuration Lab (Level 2) is mastered.

## 🧩 Domain Analysis
### Domain 2.0: Network Implementation
*   **2.1 (Know):** Routing Tech (Theory) -> Groundwork for...
*   **2.2 (Do):** Switching Config (Skill)
*   **2.3 (Do):** Wireless Config (Skill)
*   **2.4 (Know):** Physical Install (Context) -> Context for 2.2/2.3 physical deployment.

*Insight:* Objectives 2.1 and 2.4 are the "Bookends" of knowledge that support the "Core Actions" of 2.2 and 2.3.

## 🛡️ Domain 5.0: The Final Boss (Composite Skills)
*Hypothesis: Troubleshooting is not a separate domain. It is the integration test for Domains 1-4.*

You cannot "study" Domain 5 in isolation. It is a composite skill that requires the real-time synthesis of all previous knowledge.

### The "Full Stack" Dependency Map
| Troubleshooting Objective | Requires Mastery of... | Logic |
|---|---|---|
| **5.2 Physical/Cabling** | **1.2 (Hardware)** + **1.5 (Media)** + **2.4 (Physical Install)** | You can't fix a cable fault (5.2) if you don't know cable specs (1.5) or installation standards (2.4). |
| **5.3 Network Services** | **1.4 (Ports)** + **2.2 (Switching)** + **2.3 (Wireless)** + **3.4 (IPv4/6 Services)** | You can't fix a DHCP failure (5.3) if you don't know how DHCP works (1.4) or how to configure it (3.4). |
| **5.4 Performance** | **1.1 (OSI Model)** + **3.2 (Monitoring)** + **1.6 (Topologies)** | You can't fix "slow network" (5.4) without understanding bandwidth (1.6) or reading monitoring tools (3.2). |

### ⚔️ Strategy Implication
**"Stress-Test" the Fundamentals.**
We do not just "read" Domain 5 chapters. We use Domain 5 scenarios to **audit** our understanding of Domains 1-4.
*   *If you fail a 5.3 DHCP Question:* Do not just review the troubleshooting steps. Go back and re-lab Objective 3.4 (Configure DHCP).
*   *The Pivot:* Domain 5 is our **Diagnostic Tool** for the rest of the study plan.

## 🌲 The Three Trees of Troubleshooting (The Lenses)
Domain 5 isn't just a list; it is structured into three distinct "Trees" that all other domains feed into. This allows for **"Lens Locking"**—studying only the attributes of a topic relevant to its specific tree.

### Tree 1: The Physical Reality (Obj 5.2) [PHY]
*   **Focus:** Hardware, Cables, Power, Interference.
*   **Dependencies:** D1.2 (Hardware), D2.4 (Install).
*   **Tools:** Cable Tester, OTDR, Multimeter.
*   **Test:** "Given a scenario, diagnose a 'Split Pair' or 'Crosstalk'."

### Tree 2: The Logical Reality (Obj 5.3) [LOG]
*   **Focus:** Protocols, Addressing, Services, Handshakes.
*   **Dependencies:** D1.4 (Protocols), D2.1-2.3 (Addressing), D3.4 (Services).
*   **Tools:** Packet Tracer, Wireshark, CLI (`ipconfig`, `ping`).
*   **Test:** "Given a scenario, diagnose why a PC has an APIPA address."

### Tree 3: The Performance Reality (Obj 5.4) [PRF]
*   **Focus:** Flow, Capacity, Latency, Jitter.
*   **Dependencies:** D1.6 (Metrics), D3.2 (Monitoring).
*   **Tools:** SNMP, NetFlow, Speed Tests.
*   **Test:** "Given a scenario, explain why the VoIP call is dropping."

## 📐 The 3D Coordinate System (The Ultimate Schema)
Every single exam objective can be mapped to a 3D coordinate. This transforms the study plan from a linear list into a structured database.

1.  **Vertical Axis (The Lens):** Which Tree does it feed? ([PHY], [LOG], [PRF])
2.  **Horizontal Axis (The Tool):** What 5.5 instrument inspects it?
3.  **Depth Axis (The Method):** Where does it fit in the 5.1 lifecycle (Identify → Theory → Test)?

### The "Wrapper" Layers (5.1 & 5.5)
Objectives 5.1 and 5.5 are not "topics" to be studied separately. They are **Attributes** of every other topic.
*   **5.1 (Methodology):** The **Operating System** (Process).
*   **5.5 (Tools):** The **Toolbar** (Instrument).

**Example Mapping: "VLANs (802.1Q)"**
*   **Lens:** [LOG] (Logical Tree 5.3) -> Failure Mode: Mismatched Native VLANs.
*   **Tool:** `show interfaces switchport` (CLI) / Wireshark.
*   **Method:** "Test the Theory" -> If ping fails, is the Tag missing?
