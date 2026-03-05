# Network+ N10-009: 3D Objective Mapping Report

> **Generated:** 2026-02-05
> **Source Prompt:** `MetaPrompt_3D_Mapping.md`
> **Methodology:** Verb Cipher Protocol + Three Trees + 3D Coordinate Schema
> **Coverage:** All 25 N10-009 objectives

---

## 1. Notation Conventions

### Lens Notation
- **`[PHY]`** = Physical Reality (Tree 5.2) — failure mode is hardware, cabling, power, RF, environmental
- **`[LOG]`** = Logical Reality (Tree 5.3) — failure mode is wrong address, wrong protocol, misconfigured service, auth failure
- **`[PRF]`** = Performance Reality (Tree 5.4) — failure mode is slow, congested, jittery, high latency, packet loss
- **Primary lens** is listed first. Secondary lenses follow after a comma.
- **`AXIS`** = This objective IS part of the coordinate system, not a mappable topic.

### Level Notation
- **L1** = Level 1 (Knowledge) — Verb Cipher: Flashcards only
- **L2** = Level 2 (Application) — Verb Cipher: Configuration labs
- **L3** = Level 3 (Analysis) — Verb Cipher: Break-Fix scenarios
- **L1-W** = Level 1, Wrapper layer (5.1 Methodology — part of the coordinate system)
- **L2-W** = Level 2, Wrapper layer (5.5 Tools — part of the coordinate system)

### Method Stage Notation (from Objective 5.1)
- **S1** = Identify the Problem
- **S2** = Establish a Theory of Probable Cause
- **S3** = Test the Theory
- **S4** = Establish a Plan of Action
- **S5** = Implement the Solution / Verify Full System Functionality
- **S6** = Document Findings
- **S1-S6** = Full Lifecycle (all stages apply — used for L3 objectives)

### Tool Format
- Physical tools in plain text (e.g., Cable Tester)
- CLI commands in backticks (e.g., `show vlan brief`)
- Software tools capitalized (e.g., Wireshark)
- Filter/context in parentheses (e.g., Wireshark (`bootp` filter))

### Void Flag
- **N/A** = Not applicable (L1 objectives do not require labs)
- **OK** = Cengage provides adequate lab coverage
- **GAP** = CompTIA requires depth that Cengage does not provide — custom lab needed
- **CHECK** = Needs verification against Cengage Hands-On Projects

### Dependency Format
- Direct prerequisites only (one level up in the skill tree)
- Format: comma-separated objective IDs

---

## 2. Master 3D Mapping Table

### Domain 1.0: Networking Concepts (23%) — 8 Objectives

| Obj ID | Title | Verb | Level | Primary Lens | Secondary Lens(es) | Primary Tool (5.5) | Verification Tool | Method Stage (5.1) | Dependencies | Void Flag |
|--------|-------|------|-------|--------------|--------------------|--------------------|-----------------|--------------------|-------------|-----------|
| 1.1 | OSI Reference Model | Explain | L1 | `[LOG]` | `[PHY]` (Layer 1) | Wireshark (layer-by-layer decode) | — | S1 (OSI is the mental model for problem identification) | — | N/A |
| 1.2 | Networking Appliances & Devices | Compare | L1 | `[PHY]` | `[LOG]` (device function) | Visual Inspection / `show version` | — | S1 (device identification is step 1 of troubleshooting) | — | N/A |
| 1.3 | Cloud Concepts & Connectivity | Summarize | L1 | `[LOG]` | — | Cloud Dashboard / Management Console | — | S1 (understanding service model classifies issues) | — | N/A |
| 1.4 | Ports, Protocols, Services, Traffic | Explain | L1 | `[LOG]` | — | `netstat` / `ss` / Wireshark (port identification) | — | S2 (knowing port-to-service mapping enables theory formation) | — | N/A |
| 1.5 | Transmission Media & Cabling | Compare | L1 | `[PHY]` | `[PRF]` (cable specs determine bandwidth) | Cable Tester / OTDR / Light Meter | — | S1 (physical layer knowledge identifies Layer 1 issues) | — | N/A |
| 1.6 | Topologies, Architectures, Types | Compare | L1 | `[LOG]` | `[PHY]` (physical topology), `[PRF]` (topology affects throughput/redundancy) | Network Diagram / `traceroute` (path analysis) | — | S1 (topology knowledge determines scope of failure) | — | N/A |
| 1.7 | IPv4 Network Addressing | Use | L2 | `[LOG]` | — | `ipconfig` / `ifconfig` / Subnet Calculator | `ping` + `arp -a` (verify reachability) | S3 (assign address, test connectivity) | 1.1, 1.4 | CHECK |
| 1.8 | Modern Network Environments | Summarize | L1 | `[LOG]` | — | N/A — Conceptual (IoT, SD-WAN, BYOD are architectural) | — | S1 (modern context classifies environment-specific issues) | — | N/A |

### Domain 2.0: Network Implementation (20%) — 4 Objectives

| Obj ID | Title | Verb | Level | Primary Lens | Secondary Lens(es) | Primary Tool (5.5) | Verification Tool | Method Stage (5.1) | Dependencies | Void Flag |
|--------|-------|------|-------|--------------|--------------------|--------------------|-----------------|--------------------|-------------|-----------|
| 2.1 | Routing Technologies | Explain | L1 | `[LOG]` | — | `show ip route` / `traceroute` | — | S2 (routing knowledge enables path-based theories) | 1.1, 1.4 | N/A |
| 2.2 | Switching Technologies | Configure | L2 | `[LOG]` | `[PHY]` (port assignment) | CLI: `switchport mode trunk`, `vlan` commands | `show vlan brief` / `show mac address-table` / `show spanning-tree` | S3 (configure, then verify with show commands) | 1.2, 1.4, 1.6 | CHECK |
| 2.3 | Wireless Devices & Technologies | Configure | L2 | `[LOG]` | `[PHY]` (antenna, signal, interference), `[PRF]` (throughput, standards) | AP Management Console / Wireless Controller | Wi-Fi Analyzer (signal strength, channel) | S3 (configure AP, verify client connectivity) | 1.2, 1.5, 1.6, 4.1 | CHECK |
| 2.4 | Physical Installations | Explain | L1 | `[PHY]` | — | Visual Inspection / Environmental Monitor | — | S1 (installation standards inform physical troubleshooting) | 1.5 | N/A |

### Domain 3.0: Network Operations (19%) — 5 Objectives

| Obj ID | Title | Verb | Level | Primary Lens | Secondary Lens(es) | Primary Tool (5.5) | Verification Tool | Method Stage (5.1) | Dependencies | Void Flag |
|--------|-------|------|-------|--------------|--------------------|--------------------|-----------------|--------------------|-------------|-----------|
| 3.1 | Organizational Processes & Documentation | Explain | L1 | `[LOG]` | — | N/A — Conceptual (policies, change management, diagrams) | — | S6 (this objective IS the documentation step) | — | N/A |
| 3.2 | Network Monitoring Technologies | Use | L2 | `[PRF]` | `[LOG]` (event monitoring) | SNMP / NetFlow / Syslog / SIEM Dashboard | Baseline Comparison / Alert Validation | S1 (monitoring IS the identification step) | 1.1, 1.4, 1.6 | CHECK |
| 3.3 | Disaster Recovery Concepts | Explain | L1 | `[LOG]` | — | N/A — Conceptual (RPO, RTO, HA, backup strategies) | — | S4 (DR IS the plan of action) | 3.1 | N/A |
| 3.4 | IPv4/IPv6 Network Services | Implement | L2 | `[LOG]` | — | Wireshark (`bootp` filter) / `nslookup` / `dig` | `ipconfig /all` (DHCP), `nslookup` (DNS), `w32tm /query` (NTP) | S3 (implement service, verify it responds to queries) | 1.4, 1.7 | CHECK |
| 3.5 | Network Access & Management Methods | Compare | L1 | `[LOG]` | — | SSH Client / Console Cable / SNMP Browser | — | S1 (knowing access methods determines diagnostic path) | 1.4 | N/A |

### Domain 4.0: Network Security (14%) — 3 Objectives

| Obj ID | Title | Verb | Level | Primary Lens | Secondary Lens(es) | Primary Tool (5.5) | Verification Tool | Method Stage (5.1) | Dependencies | Void Flag |
|--------|-------|------|-------|--------------|--------------------|--------------------|-----------------|--------------------|-------------|-----------|
| 4.1 | Basic Network Security Concepts | Explain | L1 | `[LOG]` | — | N/A — Conceptual (CIA triad, AAA, zero trust) | — | S2 (security knowledge enables theory about unauthorized activity) | — | N/A |
| 4.2 | Types of Attacks & Impact | Summarize | L1 | `[LOG]` | — | Wireshark (anomalous traffic) / IDS/IPS Logs | — | S2 (attack pattern recognition enables incident theories) | 1.4, 4.1 | N/A |
| 4.3 | Network Security Features & Solutions | Apply | L2 | `[LOG]` | `[PHY]` (physical security: locks, cameras, biometrics) | Firewall CLI / `show access-lists` / VPN Client | Port Scan (verify blocked ports) / VPN Connectivity Test | S5 (apply controls, verify enforcement) | 1.4, 4.1, 4.2 | CHECK |

### Domain 5.0: Network Troubleshooting (24%) — 5 Objectives

| Obj ID | Title | Verb | Level | Primary Lens | Secondary Lens(es) | Primary Tool (5.5) | Verification Tool | Method Stage (5.1) | Dependencies | Void Flag |
|--------|-------|------|-------|--------------|--------------------|--------------------|-----------------|--------------------|-------------|-----------|
| 5.1 | Troubleshooting Methodology | Explain | L1-W | `AXIS` (Method) | — | N/A — This IS the method (mental framework) | — | ALL (S1-S6) — This DEFINES the stages | — | N/A |
| 5.2 | Cabling & Physical Interface Issues | Troubleshoot | L3 | `AXIS` (PHY Tree) | — | Cable Tester / OTDR / Multimeter / Toner Probe / Loopback Adapter | Visual Inspection + Link Lights + `show interface status` | S1-S6 (Full Lifecycle) | 1.2, 1.5, 2.4 | **GAP** (Cengage teaches cable making, not cable diagnosis — no TDR/split-pair/crosstalk break-fix labs) |
| 5.3 | Network Services Issues | Troubleshoot | L3 | `AXIS` (LOG Tree) | — | Wireshark / `nslookup` / `dig` / `ipconfig` / `ping` / `traceroute` / `arp` / CLI `show` commands | Service-specific verification (e.g., `nslookup` after DNS fix) | S1-S6 (Full Lifecycle) | 1.4, 2.2, 2.3, 3.4 | CHECK (verify Cengage has DHCP/DNS break-fix scenarios) |
| 5.4 | Performance & Connectivity Issues | Troubleshoot | L3 | `AXIS` (PRF Tree) | — | SNMP / NetFlow / `iperf` / Speed Tester / Protocol Analyzer / Bandwidth Monitor | Baseline comparison before/after fix | S1-S6 (Full Lifecycle) | 1.1, 1.6, 3.2 | CHECK (verify Cengage has bandwidth/latency break-fix scenarios) |
| 5.5 | Appropriate Tool or Protocol | Use | L2-W | `AXIS` (Tool) | — | ALL TOOLS — This IS the tool axis | Tool-specific output validation | S3 (tools are the instrument for "Test the Theory") | All L1 objectives | CHECK |

---

## 3. Dependency DAG

```
                            ╔══════════════════════════════════════╗
                            ║     LEVEL 1 — ROOT NODES            ║
                            ║     (Knowledge / Flashcards)        ║
                            ╚══════════════════════════════════════╝

    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
    │ 1.1 │  │ 1.2 │  │ 1.3 │  │ 1.4 │  │ 1.5 │  │ 1.6 │  │ 1.8 │  │ 2.4 │
    │ OSI │  │ Dev │  │Cloud│  │Port │  │Cable│  │Topo │  │ Mod │  │Inst │
    └──┬──┘  └──┬──┘  └─────┘  └──┬──┘  └──┬──┘  └──┬──┘  └─────┘  └──┬──┘
       │        │                  │        │        │                   │
       │   ┌────┤           ┌─────┼────────┤    ┌───┤                   │
       │   │    │           │     │        │    │   │                   │
       │   │    │     ┌─────┐  ┌──┐  ┌─────┐   │   │            ┌─────┐
       │   │    │     │ 2.1 │  │  │  │     │   │   │            │ 3.1 │
       │   │    │     │Route│  │  │  │     │   │   │            │Proc │
       │   │    │     └─────┘  │  │  │     │   │   │            └──┬──┘
       │   │    │              │  │  │     │   │   │               │
       │   │    │     ┌────────┤  │  │     │   │   │            ┌──┐
       │   │    │     │        │  │  │     │   │   │            │  │
    ┌──┐ ┌─┐    │  ┌──┐  ┌────┐  │  │  ┌──┐   │   │         ┌─┐  │
    │  │ │ │    │  │  │  │ 3.5│  │  │  │  │   │   │         │ │  │
    │  │ │ │    │  │  │  │Acc │  │  │  │  │   │   │         │ │  │
    │  │ │ │    │  │  │  └────┘  │  │  │  │   │   │         │ │  │
    │  │ │ │    │  │  │          │  │  │  │   │   │         │ │  │
    ├──┤ │ │    │  │  │    ┌─────┐  │  │  │   │   │    ┌────┐ │  │
    │  │ │ │    │  │  │    │ 4.1 │  │  │  │   │   │    │4.2 │ │  │
    │  │ │ │    │  │  │    │ Sec │  │  │  │   │   │    │Atk │ │  │
    │  │ │ │    │  │  │    └──┬──┘  │  │  │   │   │    └─┬──┘ │  │
    │  │ │ │    │  │  │       │     │  │  │   │   │      │    │  │
    │  │ │ │    │  │  │       │     │  │  │   │   │      │    │  │
    ╔══╧══╧═╧════╧══╧══╧═══════╧═════╧══╧══╧═══╧═══╧════╧══════╧════╧══╗
    ║               LEVEL 2 — INTERMEDIATE NODES                        ║
    ║               (Application / Configuration Labs)                  ║
    ╚═══════════════════════════════════════════════════════════════════╝

    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   1.7    │  │   2.2    │  │   2.3    │  │   3.2    │
    │ IPv4 Addr│  │ Switching│  │ Wireless │  │ Monitor  │
    │ (L2)     │  │ (L2)     │  │ (L2)     │  │ (L2)     │
    │ ← 1.1   │  │ ← 1.2   │  │ ← 1.2   │  │ ← 1.1   │
    │ ← 1.4   │  │ ← 1.4   │  │ ← 1.5   │  │ ← 1.4   │
    │          │  │ ← 1.6   │  │ ← 1.6   │  │ ← 1.6   │
    │          │  │          │  │ ← 4.1   │  │          │
    └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │              │
    ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐       │
    │   3.4    │  │   4.3    │  │          │       │
    │ Services │  │ SecApply │  │          │       │
    │ (L2)     │  │ (L2)     │  │          │       │
    │ ← 1.4   │  │ ← 1.4   │  │          │       │
    │ ← 1.7   │  │ ← 4.1   │  │          │       │
    │          │  │ ← 4.2   │  │          │       │
    └────┬─────┘  └──────────┘  └────┬─────┘       │
         │                           │              │
    ╔════╧═══════════════════════════╧══════════════╧═══╗
    ║          LEVEL 3 — LEAF NODES                     ║
    ║          (Analysis / Break-Fix Scenarios)          ║
    ║          24% of Exam Weight (Domain 5)            ║
    ╚═══════════════════════════════════════════════════╝

    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
    │      5.2       │  │      5.3       │  │      5.4       │
    │ [PHY] Physical │  │ [LOG] Logical  │  │ [PRF] Perform  │
    │ Cable/Hardware │  │ Services/Proto │  │ Speed/Connect  │
    │                │  │                │  │                │
    │ ← 1.2 (Devs)  │  │ ← 1.4 (Ports) │  │ ← 1.1 (OSI)   │
    │ ← 1.5 (Cable) │  │ ← 2.2 (Switch)│  │ ← 1.6 (Topo)  │
    │ ← 2.4 (Inst)  │  │ ← 2.3 (WiFi)  │  │ ← 3.2 (Mon)   │
    │                │  │ ← 3.4 (Svc)   │  │                │
    └────────────────┘  └────────────────┘  └────────────────┘
```

### Critical Path Nodes (Prerequisites for 3+ Downstream Objectives)

| Objective | Downstream Count | Feeds Into |
|-----------|-----------------|-----------|
| **1.4 (Ports/Protocols)** | **9** downstream | 1.7, 2.1, 2.2, 3.2, 3.4, 3.5, 4.2, 4.3, 5.3 |
| **1.1 (OSI Model)** | **4** downstream | 1.7, 2.1, 3.2, 5.4 |
| **1.2 (Devices)** | **4** downstream | 2.2, 2.3, 5.2 (+ indirect) |
| **1.6 (Topologies)** | **4** downstream | 2.2, 2.3, 3.2, 5.4 |
| **1.5 (Cabling)** | **3** downstream | 2.3, 2.4, 5.2 |
| **4.1 (Security Concepts)** | **3** downstream | 2.3, 4.2, 4.3 |

**Study Priority Implication:** Objective 1.4 (Ports, Protocols, Services) is the single most critical knowledge node. It feeds 9 of the 25 objectives. Master this first.

---

## 4. Multi-Lens Audit

### Objectives with Multiple Lens Assignments

| Obj ID | Title | Primary Lens | Secondary Lenses | Analysis |
|--------|-------|-------------|-----------------|---------|
| **1.2** | Networking Appliances | `[PHY]` | `[LOG]` | **Primary PHY:** "What hardware is this?" is the first physical identification question. **Secondary LOG:** Device function (router routes, switch switches) is a logical property. **Recommendation:** Study once, but separate the physical attributes (form factor, ports, indicators) from logical attributes (forwarding behavior, protocol support). |
| **1.5** | Transmission Media | `[PHY]` | `[PRF]` | **Primary PHY:** Cables are physical objects. **Secondary PRF:** Cable category ratings (Cat5e = 1Gbps, Cat6a = 10Gbps) and fiber modes (single-mode = long distance, multi-mode = short distance) directly determine performance characteristics. **Recommendation:** Study PHY first (connectors, construction, termination), then add PRF lens (bandwidth ratings, distance limits) as a second pass. |
| **1.6** | Topologies | `[LOG]` | `[PHY]`, `[PRF]` | **Primary LOG:** Topologies are logical designs (star, mesh, ring). **Secondary PHY:** Physical topology (how cables are actually run) may differ from logical topology. **Secondary PRF:** Topology determines redundancy paths, single points of failure, and aggregate throughput. **Recommendation:** Study LOG topology diagrams first, then map to PHY reality, then analyze PRF implications. This is a triple-lens objective but the lenses are layered, not competing. |
| **2.2** | Switching Technologies | `[LOG]` | `[PHY]` | **Primary LOG:** VLANs, STP, trunking are logical Layer 2 constructs. **Secondary PHY:** Port assignment (which physical port goes to which VLAN) bridges logical config to physical reality. **Recommendation:** Study as LOG. Physical port mapping is just the "last step" of implementation. |
| **2.3** | Wireless Technologies | `[LOG]` | `[PHY]`, `[PRF]` | **This is the most complex multi-lens objective.** **Primary LOG:** SSID config, authentication (WPA2/WPA3), encryption, RADIUS integration. **Secondary PHY:** Antenna type (omni vs. directional), channel selection, RF interference, physical AP placement. **Secondary PRF:** 802.11 standards (ax vs. ac = throughput), channel width, client density, co-channel interference. **Recommendation:** THREE separate study sessions — one per lens. PHY session: antenna/signal/interference. LOG session: auth/encryption/SSID. PRF session: standards/throughput/capacity. |
| **3.2** | Network Monitoring | `[PRF]` | `[LOG]` | **Primary PRF:** Monitoring exists to detect performance anomalies (bandwidth utilization, latency spikes, dropped packets). **Secondary LOG:** Monitoring also detects logical events (interface down, routing changes, auth failures via Syslog). **Recommendation:** Study as PRF first (what metrics to watch), then LOG (what events to alert on). |
| **4.3** | Security Solutions | `[LOG]` | `[PHY]` | **Primary LOG:** ACLs, firewall rules, VPN configs, port security, 802.1X are logical constructs. **Secondary PHY:** Physical security (locks, cameras, mantraps, cable locks) is tested as a sub-item. **Recommendation:** Study as LOG (90% of content), flag PHY sub-items for a separate flashcard set. |

### Triple-Lens Objectives (Require Multi-Pass Study)

Only **two objectives** require all three lenses:
1. **1.6 (Topologies)** — but all three lenses are L1 (flashcards only), so the cost is low
2. **2.3 (Wireless)** — this is L2 AND triple-lens, making it the **highest-complexity objective** in the exam. Budget extra time.

---

## 5. Gap Report (Void Check)

### Confirmed Gaps

| Obj ID | Level | Gap Description | Recommended Lab |
|--------|-------|----------------|----------------|
| **5.2** | L3 | **CRITICAL GAP.** Cengage teaches how to *make* a cable (terminate RJ-45, punch down patch panel) but does NOT teach how to *diagnose* a faulty cable. No labs for: TDR readings, split pair identification, crosstalk diagnosis, fiber light level testing. CompTIA explicitly requires: "Given a scenario, troubleshoot common cabling and physical interface issues." | **Custom Lab:** Build a working Ethernet segment with a Proxmox VM. Introduce faults: (1) Swap TX/RX pairs on a patch cable to create a split pair; (2) Use a damaged cable to demonstrate CRC errors visible in `show interface` counters; (3) Simulate fiber attenuation by using dirty connectors. Use Cable Tester and `show interface status` to diagnose. |

### Objectives Requiring Verification (CHECK)

| Obj ID | Level | What to Verify | Action |
|--------|-------|---------------|--------|
| 1.7 | L2 | Does Cengage provide a subnetting lab (not just math exercises)? Need: "Given a network diagram, assign correct IPs and verify connectivity." | Cross-reference Chapter Reviews + Appendix B exercises |
| 2.2 | L2 | Does Cengage have a VLAN configuration lab with trunk verification? Need: "Configure VLANs across two switches with a trunk link." | Cross-reference Chapter 7/8 Hands-On Projects |
| 2.3 | L2 | Does Cengage have a wireless configuration lab? Need: "Configure an AP with WPA2-Enterprise and verify client auth." | Cross-reference Chapter 6 Hands-On Projects |
| 3.2 | L2 | Does Cengage have an SNMP/monitoring lab? Need: "Configure SNMP polling and create a baseline dashboard." | Cross-reference Chapter 11 Hands-On Projects |
| 3.4 | L2 | Does Cengage have DHCP/DNS implementation labs? Need: "Deploy DHCP server, configure scopes, verify lease acquisition." | Cross-reference Chapter 4/5 Hands-On Projects |
| 4.3 | L2 | Does Cengage have a firewall rule / ACL lab? Need: "Configure pfSense firewall rules to permit/deny traffic by port." | Cross-reference Chapter 10/11 Hands-On Projects |
| 5.3 | L3 | Does Cengage have DHCP/DNS *troubleshooting* labs (not just config)? Need: "Given a broken DHCP scope, diagnose why clients get APIPA addresses." | Cross-reference Chapter 12 / Troubleshooting sections |
| 5.4 | L3 | Does Cengage have bandwidth/latency *troubleshooting* labs? Need: "Given a slow network, use NetFlow/SNMP to identify the bottleneck." | Cross-reference Chapter 12 / Performance sections |
| 5.5 | L2-W | Does Cengage cover all 5.5 tools hands-on? Need: Verification that cable tester, OTDR, spectrum analyzer, packet sniffer, and CLI tools all have practical exercises. | Cross-reference Appendix A tool list against chapter labs |

---

## 6. Study Sequence Recommendation

### Phase 1: Foundation Lock (Level 1 — Knowledge Nodes)

Study order based on downstream dependency count (most critical first):

| Priority | Objective | Why First | Downstream Impact |
|----------|-----------|-----------|------------------|
| **1st** | 1.4 — Ports, Protocols, Services | Feeds 9 objectives. Cannot proceed without this. | Unlocks: 1.7, 2.1, 2.2, 3.2, 3.4, 3.5, 4.2, 4.3, 5.3 |
| **2nd** | 1.1 — OSI Model | Feeds 4 objectives. The diagnostic framework. | Unlocks: 1.7, 2.1, 3.2, 5.4 |
| **3rd** | 1.2 — Devices & Appliances | Feeds 4 objectives. Must know hardware. | Unlocks: 2.2, 2.3, 5.2 |
| **4th** | 1.6 — Topologies & Architectures | Feeds 4 objectives. Network design context. | Unlocks: 2.2, 2.3, 3.2, 5.4 |
| **5th** | 1.5 — Cabling & Media | Feeds 3 objectives. Physical layer knowledge. | Unlocks: 2.3, 2.4, 5.2 |
| **6th** | 4.1 — Security Concepts | Feeds 3 objectives. Security foundation. | Unlocks: 2.3, 4.2, 4.3 |
| **7th** | 1.3, 1.8, 2.1, 2.4, 3.1, 3.3, 3.5, 4.2 | Remaining L1 objectives (no/low downstream impact) | Study as flashcard batches, no strict order needed |

### Phase 2: Skill Unlock (Level 2 — Configuration Labs)

Study order based on dependency chains (prerequisites met first):

| Priority | Objective | Prerequisites (Must Be Done) | Lab Type |
|----------|-----------|------------------------------|----------|
| **1st** | 1.7 — IPv4 Addressing | 1.1, 1.4 | Subnetting exercises + IP assignment in Proxmox VMs |
| **2nd** | 3.4 — IPv4/IPv6 Services | 1.4, 1.7 | Deploy DHCP/DNS servers in pfSense |
| **3rd** | 2.2 — Switching Config | 1.2, 1.4, 1.6 | VLAN + Trunking + STP in Proxmox virtual switch |
| **4th** | 3.2 — Network Monitoring | 1.1, 1.4, 1.6 | SNMP polling + Syslog + baseline creation |
| **5th** | 2.3 — Wireless Config | 1.2, 1.5, 1.6, 4.1 | AP configuration (WPA2/WPA3, channels) — may need physical AP |
| **6th** | 4.3 — Security Solutions | 1.4, 4.1, 4.2 | pfSense firewall rules + ACLs + VPN tunnel |
| **7th** | 5.5 — Tools (Wrapper) | All L1 | Tool familiarization labs — one per tool category |

### Phase 3: Mastery Gate (Level 3 — Break-Fix Scenarios)

This is 24% of the exam. Each scenario requires the FULL 5.1 lifecycle (Identify through Document).

| Priority | Objective | All Prerequisites Met After | Scenario Focus |
|----------|-----------|---------------------------|---------------|
| **1st** | 5.3 — [LOG] Logical Tree | Phase 2 objectives 1.7, 2.2, 2.3, 3.4 | Break DHCP scopes, misconfigure DNS, misassign VLANs, break wireless auth. Diagnose using `ipconfig`, `nslookup`, `ping`, Wireshark. |
| **2nd** | 5.4 — [PRF] Performance Tree | Phase 2 objectives 3.2 | Saturate a link, introduce latency (tc/netem), create broadcast storms. Diagnose using SNMP, NetFlow, `iperf`, baseline comparison. |
| **3rd** | 5.2 — [PHY] Physical Tree | Phase 1 objectives 1.2, 1.5, 2.4 | Swap cables, introduce faults, disconnect interfaces. Diagnose using Cable Tester, link lights, `show interface` counters. |

**Why this order:** 5.3 (Logical) has the most dependencies and covers the broadest range of sub-topics. Mastering it first exercises the largest portion of the study material. 5.4 (Performance) requires monitoring baselines established in Phase 2. 5.2 (Physical) has the fewest dependencies but the confirmed Cengage GAP — study this last to give time for custom lab development.

### Phase 4: Validation

- Run Appendix C (Practice Exam) as a diagnostic tool
- For each missed question, trace back through the 3D coordinate to identify the failing lens/tool/method
- Re-enter the appropriate Phase (1/2/3) for targeted remediation

---

## Appendix: Statistics Summary

| Metric | Count |
|--------|-------|
| Total Objectives | 25 |
| Level 1 (Knowledge — Flashcards) | 15 (60%) |
| Level 2 (Application — Config Labs) | 7 (28%) |
| Level 3 (Analysis — Break-Fix) | 3 (12%) |
| Wrapper Layers (Axis Definitions) | 2 (5.1 + 5.5) |
| Multi-Lens Objectives | 7 |
| Triple-Lens Objectives | 2 (1.6, 2.3) |
| Confirmed Gaps | 1 (5.2 — Physical Troubleshooting) |
| Pending Verification | 9 |
| Critical Path Nodes (3+ downstream) | 6 (1.4, 1.1, 1.2, 1.6, 1.5, 4.1) |

**Key Insight:** 60% of objectives are Level 1 (flashcards only). The exam's difficulty is concentrated in the remaining 40% — particularly the three Level 3 troubleshooting objectives that constitute 24% of the exam weight. The study plan should spend the *majority* of time on the 10 L2/L3 objectives, not the 15 L1 objectives.
