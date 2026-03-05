# 3D Objective Mapping Table

> Every CompTIA Network+ N10-009 objective mapped to three coordinates: Lens (failure-mode tree), Tool (diagnostic instrument), and Method (troubleshooting lifecycle stage).

---

## How to Read This Table

### Lens (Vertical Axis)
- **`[PHY]`** — Physical Reality: failure is hardware, cabling, power, environmental
- **`[LOG]`** — Logical Reality: failure is wrong address, protocol, config, or authentication
- **`[PRF]`** — Performance Reality: failure is slow, congested, jittery, or dropping packets
- **`AXIS`** — This objective IS part of the coordinate system (Domain 5 wrapper layers)

### Method Stage (Depth Axis)
- **S1** — Identify the Problem
- **S2** — Establish a Theory of Probable Cause
- **S3** — Test the Theory
- **S4** — Establish a Plan of Action
- **S5** — Implement / Verify
- **S6** — Document Findings
- **S1-S6** — Full Lifecycle (all stages)

### Level
- **L1** — Knowledge (flashcards only)
- **L2** — Application (configuration labs)
- **L3** — Analysis (break-fix scenarios)

---

## Domain 1: Networking Concepts (23%)

| Obj | Title | Verb | Level | Primary Lens | Secondary | Tool (5.5) | Method (5.1) | Dependencies |
|-----|-------|------|-------|-------------|-----------|-----------|-------------|-------------|
| 1.1 | OSI Reference Model | Explain | L1 | `[LOG]` | `[PHY]` | Wireshark (layer decode) | S1 | — |
| 1.2 | Appliances & Devices | Compare | L1 | `[PHY]` | `[LOG]` | Visual / `show version` | S1 | — |
| 1.3 | Cloud Concepts | Summarize | L1 | `[LOG]` | — | Cloud Dashboard | S1 | — |
| 1.4 | Ports, Protocols, Services | Explain | L1 | `[LOG]` | — | `netstat` / Wireshark | S2 | — |
| 1.5 | Transmission Media | Compare | L1 | `[PHY]` | `[PRF]` | Cable Tester / OTDR | S1 | — |
| 1.6 | Topologies & Architectures | Compare | L1 | `[LOG]` | `[PHY]`,`[PRF]` | Network Diagram / `traceroute` | S1 | — |
| 1.7 | IPv4 Addressing | Use | L2 | `[LOG]` | — | `ipconfig` / Subnet Calc | S3 | 1.1, 1.4 |
| 1.8 | Modern Environments | Summarize | L1 | `[LOG]` | — | Conceptual | S1 | — |

## Domain 2: Network Implementation (20%)

| Obj | Title | Verb | Level | Primary Lens | Secondary | Tool (5.5) | Method (5.1) | Dependencies |
|-----|-------|------|-------|-------------|-----------|-----------|-------------|-------------|
| 2.1 | Routing Technologies | Explain | L1 | `[LOG]` | — | `show ip route` / `traceroute` | S2 | 1.1, 1.4 |
| 2.2 | Switching Config | Configure | L2 | `[LOG]` | `[PHY]` | `show vlan brief` / `show spanning-tree` | S3 | 1.2, 1.4, 1.6 |
| 2.3 | Wireless Config | Configure | L2 | `[LOG]` | `[PHY]`,`[PRF]` | AP Console / Wi-Fi Analyzer | S3 | 1.2, 1.5, 1.6, 4.1 |
| 2.4 | Physical Installations | Explain | L1 | `[PHY]` | — | Visual / Environmental Monitor | S1 | 1.5 |

## Domain 3: Network Operations (19%)

| Obj | Title | Verb | Level | Primary Lens | Secondary | Tool (5.5) | Method (5.1) | Dependencies |
|-----|-------|------|-------|-------------|-----------|-----------|-------------|-------------|
| 3.1 | Processes & Documentation | Explain | L1 | `[LOG]` | — | Conceptual | S6 | — |
| 3.2 | Monitoring Technologies | Use | L2 | `[PRF]` | `[LOG]` | SNMP / NetFlow / Syslog | S1 | 1.1, 1.4, 1.6 |
| 3.3 | Disaster Recovery | Explain | L1 | `[LOG]` | — | Conceptual | S4 | 3.1 |
| 3.4 | IPv4/IPv6 Services | Implement | L2 | `[LOG]` | — | Wireshark (`bootp`) / `nslookup` | S3 | 1.4, 1.7 |
| 3.5 | Access & Management Methods | Compare | L1 | `[LOG]` | — | SSH Client / Console | S1 | 1.4 |

## Domain 4: Network Security (14%)

| Obj | Title | Verb | Level | Primary Lens | Secondary | Tool (5.5) | Method (5.1) | Dependencies |
|-----|-------|------|-------|-------------|-----------|-----------|-------------|-------------|
| 4.1 | Security Concepts | Explain | L1 | `[LOG]` | — | Conceptual | S2 | — |
| 4.2 | Attacks & Impact | Summarize | L1 | `[LOG]` | — | Wireshark / IDS Logs | S2 | 1.4, 4.1 |
| 4.3 | Security Solutions | Apply | L2 | `[LOG]` | `[PHY]` | `show access-lists` / Firewall CLI | S5 | 1.4, 4.1, 4.2 |

## Domain 5: Network Troubleshooting (24%)

| Obj | Title | Verb | Level | Primary Lens | Secondary | Tool (5.5) | Method (5.1) | Dependencies |
|-----|-------|------|-------|-------------|-----------|-----------|-------------|-------------|
| 5.1 | Troubleshooting Methodology | Explain | L1 | `AXIS` | — | Methodology IS the tool | ALL (S1-S6) | — |
| 5.2 | Cabling & Physical Issues | Troubleshoot | L3 | `AXIS [PHY]` | — | Cable Tester / OTDR / Multimeter | S1-S6 | 1.2, 1.5, 2.4 |
| 5.3 | Network Services Issues | Troubleshoot | L3 | `AXIS [LOG]` | — | Wireshark / `nslookup` / `ping` / CLI | S1-S6 | 1.4, 2.2, 2.3, 3.4 |
| 5.4 | Performance & Connectivity | Troubleshoot | L3 | `AXIS [PRF]` | — | SNMP / NetFlow / `iperf` | S1-S6 | 1.1, 1.6, 3.2 |
| 5.5 | Appropriate Tool | Use | L2 | `AXIS` | — | ALL tools | S3 | All L1 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Total Objectives | 25 |
| Level 1 (Flashcards) | 15 (60%) |
| Level 2 (Config Labs) | 7 (28%) |
| Level 3 (Break-Fix) | 3 (12%) |
| Multi-Lens Objectives | 7 |
| Triple-Lens Objectives | 2 (1.6, 2.3) |
| Most Connected Node | 1.4 — 9 downstream |

---

## The 3D Coordinate Example

**Topic: VLANs (802.1Q)**

| Coordinate | Value | Meaning |
|-----------|-------|---------|
| **Lens** | `[LOG]` (Tree 5.3) | Failure mode = mismatched native VLAN, missing trunk tag |
| **Tool** | `show vlan brief` / Wireshark | Inspect VLAN assignment; capture to see 802.1Q tag |
| **Method** | S3 — Test the Theory | If ping fails across subnets, is the 802.1Q tag missing? |

**Topic: Fiber Optic Cabling**

| Coordinate | Value | Meaning |
|-----------|-------|---------|
| **Lens** | `[PHY]` (Tree 5.2) | Failure mode = dirty connector, bend radius exceeded, distance limit |
| **Tool** | OTDR / Light Meter | Measure signal attenuation; locate fault distance |
| **Method** | S1 — Identify the Problem | Is there physical connectivity at Layer 1? |

**Topic: Bandwidth Saturation**

| Coordinate | Value | Meaning |
|-----------|-------|---------|
| **Lens** | `[PRF]` (Tree 5.4) | Failure mode = link utilization > 80%, queueing delay |
| **Tool** | SNMP / NetFlow | Poll interface utilization; analyze flow distribution |
| **Method** | S3 — Test the Theory | Compare current utilization against established baseline |
