# Brainstorming: Analysis Strategy & Objective Mapping

> **Purpose:** A workbench to refine the execution of the Verb Cipher Analysis. This file serves as a staging area before finalizing the Study Roadmap.
> **Reference:** `Phase_1_Roadmapping/Materials/Cengage_Materials/Extracted/Appendices/Appendix_A_Exam_Objectives.pdf`

## 🧠 Core Question
How do we efficiently map 100+ objectives to the correct cognitive depth (Level 1/2/3) without manual drudgery?

## 📊 Objective Mapping Workbench
*This table is populated by the AI Agent (Gemini) by cross-referencing the Verb Cipher Protocol against the Exam Objectives PDF.*

### Domain 1.0: Networking Concepts (23%)
| Objective ID | Objective Title | Command Verb | Cognitive Level | Notes |
|---|---|---|---|---|
| 1.1 | Explain concepts related to the Open Systems Interconnection (OSI) reference model | Explain | 🟢 Level 1 (Know) | |
| 1.2 | Compare and contrast networking appliances, devices, and functions | Compare | 🟢 Level 1 (Know) | |
| 1.3 | Summarize cloud concepts and connectivity options | Summarize | 🟢 Level 1 (Know) | |
| 1.4 | Explain common networking ports, protocols, services, and traffic types | Explain | 🟢 Level 1 (Know) | |
| 1.5 | Compare and contrast transmission media and cabling specifications | Compare | 🟢 Level 1 (Know) | |
| 1.6 | Compare and contrast network topologies, architectures, and types | Compare | 🟢 Level 1 (Know) | |
| 1.7 | Given a scenario, use appropriate IPv4 network addressing | Use | 🟡 Level 2 (Apply) | |
| 1.8 | Summarize evolving use cases for modern network environments | Summarize | 🟢 Level 1 (Know) | |

### Domain 2.0: Network Implementation (20%)
| Objective ID | Objective Title | Command Verb | Cognitive Level | Notes |
|---|---|---|---|---|
| 2.1 | Explain characteristics of routing technologies | Explain | 🟢 Level 1 (Know) | |
| 2.2 | Given a scenario, configure switching technologies and features | Configure | 🟡 Level 2 (Apply) | |
| 2.3 | Given a scenario, select and configure wireless devices and technologies | Configure | 🟡 Level 2 (Apply) | |
| 2.4 | Explain important factors of physical installations | Explain | 🟢 Level 1 (Know) | |

### Domain 3.0: Network Operations (19%)
| Objective ID | Objective Title | Command Verb | Cognitive Level | Notes |
|---|---|---|---|---|
| 3.1 | Explain the purpose of organizational processes and documentation | Explain | 🟢 Level 1 (Know) | |
| 3.2 | Given a scenario, use network monitoring technologies | Use | 🟡 Level 2 (Apply) | |
| 3.3 | Explain disaster recovery (DR) concepts | Explain | 🟢 Level 1 (Know) | |
| 3.4 | Given a scenario, implement IPv4 and IPv6 network services | Implement | 🟡 Level 2 (Apply) | |
| 3.5 | Compare and contrast network access and management methods | Compare | 🟢 Level 1 (Know) | |

### Domain 4.0: Network Security (14%)
| Objective ID | Objective Title | Command Verb | Cognitive Level | Notes |
|---|---|---|---|---|
| 4.1 | Explain the importance of basic network security concepts | Explain | 🟢 Level 1 (Know) | |
| 4.2 | Summarize various types of attacks and their impact | Summarize | 🟢 Level 1 (Know) | |
| 4.3 | Given a scenario, apply network security features, defense techniques, and solutions | Apply | 🟡 Level 2 (Apply) | |

### Domain 5.0: Network Troubleshooting (24%)
| Objective ID | Objective Title | Command Verb | Cognitive Level | Notes |
|---|---|---|---|---|
| 5.1 | Explain the troubleshooting methodology | Explain | 🟢 Level 1 (Know) | |
| 5.2 | Given a scenario, troubleshoot common cabling and physical interface issues | Troubleshoot | 🔴 Level 3 (Analyze) | |
| 5.3 | Given a scenario, troubleshoot common issues with network services | Troubleshoot | 🔴 Level 3 (Analyze) | |
| 5.4 | Given a scenario, troubleshoot common performance and connectivity issues | Troubleshoot | 🔴 Level 3 (Analyze) | |
| 5.5 | Given a scenario, use the appropriate tool or protocol to solve networking issues | Use | 🟡 Level 2 (Apply) | |

## 🧪 Experimental Strategy: Objective-Centric Extraction
**The Concept:** Textbooks are linear (history → hardware → IP addressing). The Exam is functional. By creating "Objective Extracts," we re-assemble the textbook to match the *shape of the exam*.

**The Workflow:**
1.  **Select Objective:** (e.g., "1.2 Compare and Contrast").
2.  **Identify Source Sections:** Use the Appendix A map to find *every* section in the book related to that objective.
3.  **Synthesize:** Pull only the relevant paragraphs from those disparate sections into a single "Truth Table" or "Study Packet."

**Example: Objective 1.2 Study Packet (Mockup)**
> **Mission:** Compare Routers, Switches, and Firewalls across all domains.

| Appliance | Hardware Context (Sec 1-3) | Protocol Context (Sec 4-1, 9-2) | Security Context (Sec 10-2) |
|---|---|---|---|
| **Router** | Connects disparate networks; uses serial/fiber WAN ports. | Uses Logical Addressing (IP); makes decisions based on Routing Table (OSPF/BGP). | Acts as Edge Firewall; blocks traffic via ACLs (Layer 3/4). |
| **Switch** | Connects devices on same LAN; high-density RJ45 ports; ASICs. | Uses Physical Addressing (MAC); makes decisions based on MAC Table. | Port Security; VLAN segregation; ARP Inspection. |
| **Firewall** | Dedicated security appliance; multiple interfaces (Inside/Outside/DMZ). | Can route (Layer 3) but primarily inspects State (Layer 4/5/7). | Stateful Packet Inspection (SPI); Deep Packet Inspection (DPI); VPN termination. |

*This single table replaces 40 pages of scattered reading.*

**Why this works:** Instead of reading Chapter 1 and waiting 8 chapters to learn about WAN Routers (Chapter 9), we pull the WAN Router info *into* the Chapter 1 Router discussion immediately. This creates a complete "Device Definition" file.

## 🧩 Advanced Strategy: Faceted Knowledge Matrices
**The Concept:** Objects in networking are not static; they change based on the "Contextual Lens" you view them through.
*   **The Problem:** A "Router" in Chapter 1 (Hardware) looks different than a "Router" in Chapter 4 (IP Logic) or Chapter 10 (Security Target).
*   **The Solution:** Build a **Faceted Matrix** for key entities.

**Example Matrix: The "Router" Entity**
| Facet (Lens) | Source Sections | Key Questions to Answer |
|---|---|---|
| **Hardware** | 1-3, 7-1 | What are the physical interfaces? What is the backplane speed? |
| **Protocol (Logic)** | 4-1, 9-2 | How does it handle Layer 3 IP packets? What is the Routing Table? |
| **Connectivity (WAN)** | 9-1 | How does it terminate T1/Fiber/MPLS connections? |
| **Security (Enforcement)** | 10-2, 11-2 | How do ACLs work? How does it act as a choke point? |

**Cognitive Goal:**
By pre-assembling this matrix, you allow your brain (or an AI) to "query" the object from any angle.

### Dynamic Lens Inference
**The Insight:** The lenses are not static. The specific "Compare and Contrast" question *dictates* which lenses matter.
*   **Scenario A:** "Compare Switch vs. Router regarding **Traffic Segmentation**."
    *   *Inferred Lens:* Broadcast Domains vs. Collision Domains.
    *   *Table Data:* Switch breaks Collision Domains; Router breaks Broadcast Domains.
*   **Scenario B:** "Compare Switch vs. Router regarding **Security**."
    *   *Inferred Lens:* ACLs vs. Port Security.
    *   *Table Data:* Switch uses MAC filtering/802.1x; Router uses IP ACLs.

**Conclusion:** We do not just build "one giant table." We build the **capability** to generate specific tables on demand based on the implied context of the exam objective.

## 🚀 The 3D Mapping Strategy ("The Mapping Run")
To operationalize the "Three Trees" insight from `Objective_Architecture_Brainstorming.md`, we will run a Deep Research campaign to tag every objective in Domains 1-4 with a **Tri-Lens Coordinate**.

### The 3D Coordinate Schema
Every Objective will be mapped to a row in this master table:

| Objective | Lens (Tree) | Tool (Obj 5.5) | Method (Obj 5.1) |
|---|---|---|---|
| *The Topic* | *[PHY], [LOG], or [PRF]* | *The instrument used to test it* | *The stage in the troubleshoot lifecycle* |

**Lens Definitions:**
*   **[PHY] Physical Lens:** Feeds Tree 5.2. Focus on Hardware, Connectors, Physics.
*   **[LOG] Logical Lens:** Feeds Tree 5.3. Focus on Packets, Addresses, Handshakes.
*   **[PRF] Performance Lens:** Feeds Tree 5.4. Focus on Capacity, Latency, Flow.

**Goal:** This creates a "Relevance Filter." When studying a [PHY] topic, we ignore the Logical attributes and focus solely on Physical failure modes.

## 📚 CTT+ Cognitive Definitions
*Extracted directly from `CTT_Reference_Materials.pdf`.*

- **Knowledge:** A component of the cognitive domain in Bloom’s Taxonomy. This element is evident when a person can recall specific information, technical terms, and concepts, and answer questions about the technology.
- **Comprehension:** A component of the cognitive domain in Bloom’s Taxonomy. Comprehension is sometimes referred to as understanding, and is expressed through an understanding of the technical information and the ability of the learner to explain this understanding.
- **Application:** A component of the cognitive domain in Bloom’s Taxonomy. Application of knowledge is expressed by taking existing comprehension and applying it to new scenarios and problems.
- **Analysis:** A component of the cognitive domain in Bloom’s Taxonomy. Analysis in the cognitive domain is demonstrated by examining a problem or scenario and thinking through its root causes and causal factors.

## 💭 Strategy Notes
- **Critical Pattern:** Domain 5.0 (Network Troubleshooting) has the **highest exam weight (24%)** and also contains the **highest concentration of Level 3 (Analysis) cognitive tasks**. This represents the highest risk/reward area of the exam.
- **Refining the "Void Check":** We need to scan Cengage specifically for labs covering Objectives 5.2, 5.3, and 5.4. These are the critical Level 3 tasks.
- **Automation:** The script successfully extracted the structure. The "Given a scenario..." prefix masked the true verb in many cases (Use, Configure, Implement, Troubleshoot).
- **Integration:** The `CTT_Reference_Materials` confirms that "Troubleshoot" requires Analysis (Level 3), which matches our cipher.
