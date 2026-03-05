# The Three Trees of Troubleshooting

> Domain 5.0 is not a list of topics. It is three distinct failure-mode "trees" that all other domains feed into.

---

## The Insight: Domain 5 as "Master Key"

If you could masterfully solve any Domain 5 question, you would have already mastered all other domains. Troubleshooting requires:
- Comparing **current state** against **ideal state** (requires Domain 1 knowledge)
- Knowing **how it was built** (requires Domain 2 implementation skills)
- Understanding **how it should be running** (requires Domain 3 operations knowledge)
- Recognizing **when something is compromised** (requires Domain 4 security awareness)

Domain 5 is the **integration test** for the entire exam.

---

## The Three Trees

### Tree 1: Physical Reality `[PHY]` — Objective 5.2

**Focus:** Hardware, Cables, Power, Interference, Environmental.

**The Question:** *Is the thing broken, dead, or miswired?*

**Failure Modes:**
- Cable fault (split pair, crosstalk, open, short)
- Interface down (no link light, speed/duplex mismatch)
- Power issue (PoE failure, UPS failure)
- Environmental (heat, EMI, distance exceeded)

**Diagnostic Tools:**
- Cable Tester (wiremap, continuity)
- OTDR (fiber distance/fault location)
- Multimeter (voltage/continuity)
- Toner Probe (cable tracing)
- Visual Inspection + Link Lights
- `show interface status` (error counters, CRC errors)

**Dependency Prerequisites:**
| Prerequisite | What It Provides |
|-------------|-----------------|
| 1.2 (Devices) | Know what the hardware IS |
| 1.5 (Cabling) | Know cable specs, connector types, distance limits |
| 2.4 (Physical Install) | Know installation standards, rack placement, cable management |

---

### Tree 2: Logical Reality `[LOG]` — Objective 5.3

**Focus:** Protocols, Addressing, Services, Handshakes, Authentication.

**The Question:** *Is the config wrong, the address wrong, or the service down?*

**Failure Modes:**
- IP address misconfiguration (wrong subnet, duplicate IP, no gateway)
- DNS failure (wrong server, missing record, cache poisoning)
- DHCP failure (exhausted scope, wrong gateway option, rogue server)
- VLAN misconfiguration (wrong VLAN assignment, trunk mismatch, native VLAN mismatch)
- Authentication failure (wrong credentials, expired certificate, RADIUS unreachable)
- Routing failure (missing route, wrong metric, asymmetric path)

**Diagnostic Tools:**
- `ipconfig` / `ifconfig` (address verification)
- `ping` (Layer 3 reachability)
- `traceroute` / `tracert` (path analysis)
- `nslookup` / `dig` (DNS resolution)
- `arp -a` (Layer 2-to-3 mapping)
- Wireshark (packet capture and protocol decode)
- CLI `show` commands (`show vlan brief`, `show ip route`, `show mac address-table`)

**Dependency Prerequisites:**
| Prerequisite | What It Provides |
|-------------|-----------------|
| 1.4 (Ports/Protocols) | Know which port maps to which service (DHCP=67/68, DNS=53, etc.) |
| 2.2 (Switching) | Know correct VLAN/trunk configuration |
| 2.3 (Wireless) | Know correct wireless auth/encryption config |
| 3.4 (Network Services) | Know how to implement DHCP/DNS/NTP correctly |

---

### Tree 3: Performance Reality `[PRF]` — Objective 5.4

**Focus:** Flow, Capacity, Latency, Jitter, Packet Loss.

**The Question:** *Does the thing work, but is it slow, congested, or dropping packets?*

**Failure Modes:**
- Bandwidth saturation (utilization > 80%)
- High latency (distance, processing delay, queuing)
- Jitter (inconsistent latency — kills VoIP/video)
- Packet loss (congestion, buffer overflow, errors)
- Broadcast storm (STP failure, loop)
- Bottleneck (single slow link in the path)
- QoS misconfiguration (wrong traffic priority)

**Diagnostic Tools:**
- SNMP (polling interface utilization, error counters)
- NetFlow / sFlow (traffic flow analysis)
- `iperf` (bandwidth testing between endpoints)
- Speed Tester (throughput measurement)
- Protocol Analyzer (retransmission analysis)
- Bandwidth Monitor / Dashboard (baseline comparison)

**Dependency Prerequisites:**
| Prerequisite | What It Provides |
|-------------|-----------------|
| 1.1 (OSI Model) | Layer isolation for identifying where performance degrades |
| 1.6 (Topologies) | Know network design — where bottlenecks can form |
| 3.2 (Monitoring) | Know how to read monitoring dashboards and baselines |

---

## The Wrapper Layers

Objectives 5.1 and 5.5 are NOT standalone study topics. They are **attributes** of every other topic.

### 5.1 — The Troubleshooting Methodology (The Operating System)

This is the **process** applied to every troubleshooting scenario:

1. **Identify the Problem** — Gather information, question users, determine scope
2. **Establish a Theory of Probable Cause** — Top-down (OSI Layer 7→1) or bottom-up (Layer 1→7)
3. **Test the Theory** — Confirm by reproducing or isolating
4. **Establish a Plan of Action** — Define the fix and its potential side effects
5. **Implement the Solution / Verify Full Functionality** — Apply the fix, test everything
6. **Document Findings** — Record the issue, root cause, and resolution

You do not "study the methodology" in isolation. You **apply the methodology** to every Tree's scenarios.

### 5.5 — The Diagnostic Tools (The Toolbar)

These are the **instruments** used to execute each methodology step. You do not "study ping." You study **"ping as a diagnostic tool for Layer 3 reachability when troubleshooting a [LOG] tree problem."**

| Tool Category | Instruments | Primary Tree |
|--------------|------------|-------------|
| Physical | Cable Tester, OTDR, Multimeter, Toner Probe, Loopback Adapter | `[PHY]` |
| Logical/Software | Wireshark, `ping`, `traceroute`, `nslookup`, `ipconfig`, `netstat`, `arp`, CLI `show` | `[LOG]` |
| Performance | SNMP, NetFlow, `iperf`, Speed Tester, Protocol Analyzer | `[PRF]` |

---

## The Full Dependency DAG

### Level 1 → Level 2 → Level 3 Skill Progression

```
LEVEL 1 (Knowledge — Flashcards)
├── 1.4 Ports/Protocols ──────┬──→ 1.7 IPv4 Addressing ──→ 3.4 Network Services ──→ 5.3 [LOG]
│                              ├──→ 2.2 Switching ─────────────────────────────────→ 5.3 [LOG]
│                              ├──→ 3.2 Monitoring ────────────────────────────────→ 5.4 [PRF]
│                              ├──→ 3.5 Access Methods
│                              ├──→ 4.2 Attacks ──→ 4.3 Security Solutions
│                              └──→ 4.3 Security Solutions
│
├── 1.1 OSI Model ────────────┬──→ 1.7 IPv4 Addressing
│                              ├──→ 2.1 Routing
│                              ├──→ 3.2 Monitoring ────────────────────────────────→ 5.4 [PRF]
│                              └───────────────────────────────────────────────────→ 5.4 [PRF]
│
├── 1.2 Devices ──────────────┬──→ 2.2 Switching ─────────────────────────────────→ 5.3 [LOG]
│                              ├──→ 2.3 Wireless ──────────────────────────────────→ 5.3 [LOG]
│                              └───────────────────────────────────────────────────→ 5.2 [PHY]
│
├── 1.6 Topologies ───────────┬──→ 2.2 Switching
│                              ├──→ 2.3 Wireless
│                              ├──→ 3.2 Monitoring
│                              └───────────────────────────────────────────────────→ 5.4 [PRF]
│
├── 1.5 Cabling ──────────────┬──→ 2.3 Wireless
│                              ├──→ 2.4 Physical Install ─────────────────────────→ 5.2 [PHY]
│                              └───────────────────────────────────────────────────→ 5.2 [PHY]
│
├── 4.1 Security Concepts ────┬──→ 2.3 Wireless
│                              ├──→ 4.2 Attacks
│                              └──→ 4.3 Security Solutions
│
└── (1.3, 1.8, 2.1, 2.4, 3.1, 3.3, 3.5, 4.2 — Low/no downstream dependencies)
```

### Critical Path Node: Objective 1.4

Objective 1.4 (Ports, Protocols, Services, Traffic Types) feeds **9 downstream objectives**. It is the single most important knowledge node in the entire exam. If you master one thing first, master this.

---

## Study Strategy: The "Stress-Test" Method

Do not just "read" Domain 5 chapters. Use Domain 5 scenarios to **audit** your understanding of Domains 1-4.

**If you fail a 5.3 DHCP question:**
- Do not just review the troubleshooting steps
- Go back and re-lab Objective 3.4 (Implement DHCP)
- Review Objective 1.4 (DHCP ports 67/68)

**If you fail a 5.4 performance question:**
- Do not just review monitoring tools
- Go back and review Objective 1.6 (Topologies — where can bottlenecks form?)
- Re-lab Objective 3.2 (Monitoring — can you read the dashboard?)

Domain 5 is your **diagnostic tool** for the rest of the study plan.
