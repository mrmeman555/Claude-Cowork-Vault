# Skill Trees: Dependency Visualizations

> Mermaid.js diagrams showing the prerequisite chains between N10-009 objectives.

---

## The Switching Skill Tree

The canonical example of how Level 1 knowledge "unlocks" Level 2 skills, which in turn "unlock" Level 3 mastery.

```mermaid
graph TD
    subgraph L1_Knowledge [Level 1: Knowledge — Flashcards]
        obj1_2["1.2 Devices & Appliances<br/>Verb: Compare"]
        obj1_4["1.4 Ports & Protocols<br/>Verb: Explain"]
        obj1_6["1.6 Topologies<br/>Verb: Compare"]
    end

    subgraph L2_Application [Level 2: Application — Config Lab]
        obj2_2["2.2 Switching Config<br/>Verb: Configure"]
    end

    subgraph L3_Analysis [Level 3: Analysis — Break-Fix]
        obj5_3["5.3 Network Services TS<br/>Verb: Troubleshoot"]
    end

    obj1_2 -->|"Must know what a switch IS"| obj2_2
    obj1_4 -->|"Must know Layer 2 protocols"| obj2_2
    obj1_6 -->|"Must know WHERE it fits"| obj2_2
    obj2_2 -->|"Must know correct config to detect misconfig"| obj5_3
```

---

## The Complete Dependency DAG

All 25 objectives mapped by skill level and prerequisite chains.

```mermaid
graph LR
    subgraph Domain1 [Domain 1: Concepts]
        obj1_1["1.1 OSI"]
        obj1_2["1.2 Devices"]
        obj1_3["1.3 Cloud"]
        obj1_4["1.4 Ports"]
        obj1_5["1.5 Cabling"]
        obj1_6["1.6 Topologies"]
        obj1_7["1.7 IPv4 Addr"]
        obj1_8["1.8 Modern"]
    end

    subgraph Domain2 [Domain 2: Implementation]
        obj2_1["2.1 Routing"]
        obj2_2["2.2 Switching"]
        obj2_3["2.3 Wireless"]
        obj2_4["2.4 Physical"]
    end

    subgraph Domain3 [Domain 3: Operations]
        obj3_1["3.1 Processes"]
        obj3_2["3.2 Monitoring"]
        obj3_3["3.3 DR"]
        obj3_4["3.4 Services"]
        obj3_5["3.5 Access"]
    end

    subgraph Domain4 [Domain 4: Security]
        obj4_1["4.1 Concepts"]
        obj4_2["4.2 Attacks"]
        obj4_3["4.3 Solutions"]
    end

    subgraph Domain5 [Domain 5: Troubleshooting]
        obj5_2["5.2 PHY Tree"]
        obj5_3["5.3 LOG Tree"]
        obj5_4["5.4 PRF Tree"]
    end

    obj1_1 --> obj1_7
    obj1_1 --> obj2_1
    obj1_1 --> obj3_2
    obj1_1 --> obj5_4

    obj1_2 --> obj2_2
    obj1_2 --> obj2_3
    obj1_2 --> obj5_2

    obj1_4 --> obj1_7
    obj1_4 --> obj2_2
    obj1_4 --> obj3_2
    obj1_4 --> obj3_4
    obj1_4 --> obj3_5
    obj1_4 --> obj4_2
    obj1_4 --> obj4_3
    obj1_4 --> obj5_3

    obj1_5 --> obj2_3
    obj1_5 --> obj2_4
    obj1_5 --> obj5_2

    obj1_6 --> obj2_2
    obj1_6 --> obj2_3
    obj1_6 --> obj3_2
    obj1_6 --> obj5_4

    obj1_7 --> obj3_4

    obj2_2 --> obj5_3
    obj2_3 --> obj5_3
    obj2_4 --> obj5_2

    obj3_1 --> obj3_3
    obj3_2 --> obj5_4
    obj3_4 --> obj5_3

    obj4_1 --> obj2_3
    obj4_1 --> obj4_2
    obj4_1 --> obj4_3
    obj4_2 --> obj4_3
```

---

## The Three Trees: Convergence View

Shows how Domains 1-4 feed into the three Domain 5 troubleshooting trees.

```mermaid
graph BT
    subgraph PHY_Tree [PHY Tree — 5.2 Physical]
        obj5_2_node["5.2 Troubleshoot Cabling & Physical"]
    end

    subgraph LOG_Tree [LOG Tree — 5.3 Logical]
        obj5_3_node["5.3 Troubleshoot Network Services"]
    end

    subgraph PRF_Tree [PRF Tree — 5.4 Performance]
        obj5_4_node["5.4 Troubleshoot Performance"]
    end

    D1_2["1.2 Devices"] --> obj5_2_node
    D1_5["1.5 Cabling"] --> obj5_2_node
    D2_4["2.4 Physical Install"] --> obj5_2_node

    D1_4["1.4 Ports/Protocols"] --> obj5_3_node
    D2_2["2.2 Switching"] --> obj5_3_node
    D2_3["2.3 Wireless"] --> obj5_3_node
    D3_4["3.4 Network Services"] --> obj5_3_node

    D1_1["1.1 OSI Model"] --> obj5_4_node
    D1_6["1.6 Topologies"] --> obj5_4_node
    D3_2["3.2 Monitoring"] --> obj5_4_node
```

---

## Study Order Priority

Based on downstream dependency count:

```mermaid
graph TD
    subgraph Priority1 [Priority 1: Study First]
        P1_4["1.4 Ports/Protocols — 9 downstream"]
    end

    subgraph Priority2 [Priority 2: Study Second]
        P1_1["1.1 OSI — 4 downstream"]
        P1_2["1.2 Devices — 4 downstream"]
        P1_6["1.6 Topologies — 4 downstream"]
    end

    subgraph Priority3 [Priority 3: Study Third]
        P1_5["1.5 Cabling — 3 downstream"]
        P4_1["4.1 Security — 3 downstream"]
    end

    subgraph Priority4 [Priority 4: Remaining L1]
        PRest["1.3, 1.8, 2.1, 2.4, 3.1, 3.3, 3.5, 4.2"]
    end

    Priority1 --> Priority2
    Priority2 --> Priority3
    Priority3 --> Priority4
```
