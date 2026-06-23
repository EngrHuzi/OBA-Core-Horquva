# OBA Core — Mukammal Documentation (Roman Urdu)

**Horquva Engineering · 2026**

---

## Table of Contents

1. [OBA Core Kya Hai?](#1-oba-core-kya-hai)
2. [Architecture Overview](#2-architecture-overview)
3. [Ontology Layer](#3-ontology-layer)
4. [Relationship Layer](#4-relationship-layer)
5. [Context Intelligence Layer](#5-context-intelligence-layer)
6. [Voice Agent Context Layer](#6-voice-agent-context-layer)
7. [Phase 1 — Modules 01-10](#7-phase-1)
8. [Phase 2 — Platform Foundation](#8-phase-2)
9. [Phase 3 — Governance & Accountability](#9-phase-3)
10. [Phase 4 — Executive Avatar & Voice](#10-phase-4)
11. [Phase 5 — Organizational Scale](#11-phase-5)
12. [Backend API Routes](#12-backend-api-routes)
13. [Kaise Chalayein](#13-kaise-chalayein)

---

## 1. OBA Core Kya Hai?

OBA Core ka matlab hai **Organizational Brain Analysis**. Ye ek enterprise-grade intelligence engine hai jo automatically discover karta hai, map karta hai, aur analyze karta hai har AI agent jo organization ke andar kaam kar raha hai.

**Ye teen sawaalat ka jawaab deta hai jo koi organization abhi tak nahi de pa rahi:**

1. **Har AI agent ka malik kaun hai?** (Ownership)
2. **Agar ek agent fail ho jaye to kya tootega aur kitna bura hoga?** (Dependencies)
3. **Agar koi key person chala jaye to organization pe kya asar hoga?** (Risk)

Ye sab kuch seconds mein ho jata hai — full risk scoring, cascade simulation, aur prioritized action plans ke saath.

---

## 2. Architecture Overview

OBA Core **paanch (5) layers** pe build hai:

```
Data Fabric
    ↓
Ontology Layer (Kya kya exist karta hai)
    ↓
Relationship Layer (Sab kaise juda hai)
    ↓
Knowledge Graph
    ↓
Context Layer (Real-time context)
    ↓
Modules Generate Signals
    ↓
Intelligence Engines → Reasoning
    ↓
Truth Layer → Executive Cognition
    ↓
One Organizational Truth
```

**Important baat:** Ab modules decisions nahi lete. Wo sirf signals generate karte hain. Truth Layer final decision leta hai.

---

## 3. Ontology Layer

**File:** `modules/ontology_layer.py`
**Route:** `GET /api/ontology/intelligence`

### Ye Kya Karta Hai?

Ontology Layer **Organizational Brain ka vocabulary** hai. Ye define karta hai ki organization mein kya kya exist karta hai — har entity type, har relationship type, aur unke rules.

### Entity Types (6 hain):

| Type | Matlab | Example |
|------|--------|---------|
| **Human** | Organization ka koi bhi insaan | Robert, Sarah, Lisa |
| **Team** | Logon ka group jo ek domain pe kaam karta hai | Sales Team, IT Team |
| **Agent** | AI agent jo automated tasks karta hai | Lead Scoring Agent |
| **System** | AI tool ya platform | ChatGPT, Claude, GitHub Copilot |
| **Workflow** | Business process — steps ka sequence | Lead Generation Workflow |
| **Knowledge** | Policies, documentation, runbooks | AI Agent Ownership Policy |

### Relationship Types (12 hain):

| Relationship | Matlab | Example |
|-------------|--------|---------|
| **owns** | Kisi ka paas kisi cheez ki ownership hai | Robert owns Lead Scoring Agent |
| **depends_on** | Ek entity doosre pe depend karti hai | Lead Scoring Agent depends on ChatGPT |
| **uses** | Koi workflow ya agent koi tool use karta hai | Lead Generation uses ChatGPT |
| **monitors** | Ek entity doosre ko monitor karti hai | Compliance Monitor monitors Payroll |
| **feeds** | Ek entity doosre ko data deti hai | Support Ticket feeds Customer Feedback |
| **triggers** | Ek entity doosre ko activate karti hai | Onboarding triggers Payroll |
| **backs_up** | Ek entity doosre ka backup hai | Data Backup Agent backs up CRM Sync |
| **governs** | Koi policy kisi entity pe apply hoti hai | Ownership Policy governs all agents |
| **collaborates_with** | Do entities mil kaam karti hain | Robert collaborates with Sarah |
| **sequential** | Do agents sequence mein chalte hain | Lead Scoring → Lead Qualification |
| **participates_in** | Koi workflow mein hissa leta hai | Robert participates in Lead Generation |
| **owned_by** | Entity kisi ki ownership mein hai | Agent owned_by Robert |

### Sunrise Care Data:

- **43 entities** register hue (15 agents, 8 humans, 8 knowledge, 5 systems, 7 workflows)
- **115 relationships** map hui
- **0 validation errors** — sab entities apne type definitions ke according hain

### Code Kaise Kaam Karta Hai:

```python
# Ontology banane ka code
ontology = build_ontology(data)  # data/sunrise_care.json se data padhta hai

# Entity types define karte hain
ENTITY_TYPES = {
    "human": EntityType(name="human", ...),
    "agent": EntityType(name="agent", ...),
    # ... baaki types
}

# Relationship types define karte hain
RELATIONSHIP_TYPES = {
    "owns": RelationshipType(name="owns", source_types=["human"], ...),
    # ... baaki relationships
}

# Registry mein sab register karta hai
registry = OntologyRegistry()
registry.register_entity_type(...)
registry.add_entity(...)
registry.add_relationship(...)
registry.validate_all()  # Sab entities validate hoti hain
```

---

## 4. Relationship Layer

**File:** `modules/relationship_layer.py`
**Route:** `GET /api/relationship/intelligence`

### Ye Kya Karta Hai?

Relationship Layer **entity connections ka graph** banata hai aur use navigate karta hai. Ye batata hai ki kaun kis se juda hai, kitna important hai, aur agar ek node hat jaye to kya hoga.

### Key Features:

1. **Graph Traversal** — BFS/DFS se graph navigate karta hai
2. **Shortest Path** — Do entities ke beech shortest path dhundhta hai
3. **Bottleneck Detection** — Sabse zyada important nodes dhundhta hai
4. **Cycle Detection** — Circular dependencies check karta hai
5. **Centrality Analysis** — Har node ka importance calculate karta hai
6. **Isolated Nodes** — Akeli nodes dhundhta hai jo kisi se judi nahi

### Code Kaise Kaam Karta Hai:

```python
# Relationship graph banata hai
graph = build_relationship_graph(ontology)

# BFS traversal — shortest path
path = graph.bfs("agent_001", "agent_005")
# Result: ["agent_001", "agent_002", "agent_004", "agent_005"]

# Sab paths dhundhta hai
all_paths = graph.find_all_paths("agent_001", "agent_005")

# Bottlenecks nikalta hai
betweenness = graph.calculate_betweenness()
# Jo node sabse zyada paths mein hai wo bottleneck hai

# Cycles check karta hai
cycles = graph.detect_cycles()
# Agar cycles hain to circular dependency hai

# Isolated nodes
isolated = graph.find_isolated_nodes()
# Jo nodes kisi se judi nahi
```

### Sunrise Care Results:

- **43 nodes** (entities)
- **115 edges** (relationships)
- **4 connected components** (4 alag groups)
- **3 isolated nodes** (Emma, James, Nina — kisi se judi nahi)
- **0 cycles** (koi circular dependency nahi)
- **Strongest node:** AI Agent Ownership Policy (degree 15)
- **Top bottlenecks:** Customer Feedback Agent, Email Campaign Agent, Support Ticket Agent

---

## 5. Context Intelligence Layer

**File:** `modules/context_intelligence.py`
**Route:** `GET /api/context/intelligence`

### Ye Kya Karta Hai?

Context Intelligence Layer **real-time organizational context** provide karta hai. Ye har entity, har person, aur poore organization ka context package banata hai jo Executive Avatar turant use kar sake.

### Three Types of Context Packages:

#### 1. Entity Context Package
Har entity ke baare mein complete information:
- Entity ka naam, type, owner, department
- Criticality level (LOW/MEDIUM/HIGH/CRITICAL)
- Documentation status
- Risk indicators (kya khatra hai)
- Governance status (governed hai ya nahi)
- Related entities (kis se juda hai)

#### 2. Person Context Package
Har insaan ke baare mein complete information:
- Kaunse agents uska hai
- Kaunse workflows uske hain
- Kiske liye backup hai
- Coverage gaps (kya missing hai)
- Risk level

#### 3. Organization Context
Poore organization ka summary:
- Total entities aur relationships
- Critical assets
- Orphaned assets (jinka koi malik nahi)
- Undocumented assets (jinka record nahi)
- Health score
- Executive brief

### Code Kaise Kaam Karta Hai:

```python
# Entity context banata hai
entity_ctx = build_entity_context(entity, graph, registry)
# Result: {entity_name, owner, risks, governance_status, summary}

# Person context banata hai
person_ctx = build_person_context(person, registry, graph)
# Result: {owned_agents, coverage_gaps, risk_level, summary}

# Organization context banata hai
org_ctx = build_organization_context(data, registry, entity_contexts, person_contexts)
# Result: {health_summary, orphaned_assets, top_risks, executive_brief}
```

---

## 6. Voice Agent Context Layer

**File:** `modules/context_intelligence.py` (same file mein hai)
**Route:** `GET /api/context/voice`

### Ye Kya Karta Hai?

Voice Agent Context Layer **Voice Agents ke liye semantic foundation** banata hai. Ye define karta hai ki Voice Agent organization ko kaise samajhe — entity references, conversational context, aur intent understanding.

### Key Components:

#### 1. Voice Entity Models
Har entity ke liye voice model:
- **Entity ID** — unique identifier
- **Entity Name** — naam
- **Entity Type** — human/agent/system/workflow/knowledge
- **Aliases** — alternate names jo natural language mein use ho sakti hain
- **Semantic Description** — entity ka description
- **Conversational Triggers** — kaunse questions pe ye entity relevant hai

Example:
```python
VoiceEntityModel(
    entity_id="agent_001",
    entity_name="Lead Scoring Agent",
    entity_type="agent",
    aliases=["lead scoring", "scoring agent", "lead"],
    semantic_description="An AI agent with critical criticality",
    conversational_triggers=["who owns Lead Scoring Agent", "what does Lead Scoring Agent do"]
)
```

#### 2. Intent Understanding
8 conversational intents define kiye hain:

| Intent | Trigger Words | Matlab |
|--------|--------------|--------|
| **risk_assessment** | risk, danger, threat, vulnerable | User risk samajhna chahta hai |
| **ownership_query** | owner, responsible, who owns | User jaanna chahta hai kaun malik hai |
| **dependency_analysis** | depend, break, cascade, impact | User dependencies samajhna chahta hai |
| **health_check** | health, score, status | User organization ka health jaanna chahta hai |
| **simulation** | what if, simulate, scenario | User disruption simulate karna chahta hai |
| **recommendation** | recommend, fix, improve | User actionable advice chahta hai |
| **governance** | governance, policy, compliance | User governance ke baare mein jaanna chahta hai |
| **accountability** | accountability, raci, approval | User accountability samajhna chahta hai |

#### 3. Entity Resolution Map
Natural language se entity ID mein convert karta hai:
```python
entity_resolution = {
    "robert": "human_robert",
    "lead scoring agent": "agent_001",
    "chatgpt": "tool_001",
    # ... baaki entities
}
```

---

## 7. Phase 1 — Modules 01-10

### Module 01 — Ownership Intelligence
**File:** `modules/ownership_intelligence.py`
**Route:** `GET /api/agents`, `GET /api/ownership`

**Kya karta hai:**
- Har AI agent ki ownership analyze karta hai
- Primary owner aur backup owner identify karta hai
- Orphaned agents dhundhta hai (jinka koi malik nahi)
- Owner concentration risk detect karta hai
- Risk level calculate karta hai: LOW / MEDIUM / HIGH / CRITICAL

**Risk Scoring:**
| Factor | Points |
|--------|--------|
| No owner | +40 |
| No backup | +30 |
| Not documented | +15 |
| Critical agent | +15 |
| High agent | +10 |
| Medium agent | +5 |

**Score → Risk Tier:** `< 20 = LOW` · `20-39 = MEDIUM` · `40-69 = HIGH` · `70+ = CRITICAL`

**Sunrise Care Findings:**
- Robert ke paas 5 agents hain — zero backups — highest concentration
- 2 agents orphaned: Inventory Agent, Data Backup Agent
- 9 of 15 agents ke paas backup owner nahi

---

### Module 02 — Dependency Intelligence
**File:** `modules/dependency_intelligence.py`
**Route:** `GET /api/dependencies`

**Kya karta hai:**
- Full dependency graph banata hai — kaunsa agent kis pe depend karta hai
- Single Points of Failure (SPOF) detect karta hai
- Cascade failure simulate karta hai
- Upstream depth calculate karta hai

**Sunrise Care Findings:**
- 4 SPOFs identified
- Onboarding Agent fail → 4 agents tootenge
- Inventory Agent fail → 4 agents tootenge

---

### Module 03 — Risk Intelligence
**File:** `modules/risk_intelligence.py`
**Route:** `GET /api/risks`, `GET /api/dashboard`

**Kya karta hai:**
- Module 01 + Module 02 ka data combine karta hai
- Composite risk score banata hai har agent ke liye
- CRITICAL override rule lagata hai
- **Organizational Health Score (0-100)** calculate karta hai

**Sunrise Care Findings:**
- 5 agents CRITICAL risk pe
- 6 agents HIGH risk pe
- **Health Score: 56/100 — AT RISK**

---

### Module 04 — Recommendation Engine
**File:** `modules/recommendation_engine.py`

**Kya karta hai:**
- Har risk finding ke liye specific recommendation generate karta hai
- Names the agent, names the person, names the exact action
- Priority: CRITICAL → HIGH → MEDIUM
- Top 5 Most Urgent Actions dikhata hai

**Sunrise Care Findings:**
- 12 actionable recommendations
- Top: Inventory Agent aur Data Backup Agent ko owner do
- Robert ke 5 agents redistribute karo

---

### Module 05 — What-If Simulation Engine
**File:** `modules/whatif_simulation.py`
**Route:** `GET /api/simulations/employee-leaves`, `GET /api/simulations/agent-fails`

**Kya karta hai:**
- Har possible disruption scenario simulate karta hai
- Person leaving simulation
- Agent failure simulation
- Health Score before/after dikhata hai

**Simulation Logic:**
- **Person Leaves** → unke agents ki ownership hat-ti hai (+35 risk)
- **Agent Fails** → agent maximum risk pe jaata hai (score 170)

**Sunrise Care Findings:**
- Worst: Robert jaata hai → Health Score 56 → 49
- Worst agent: Onboarding Agent fail → Health Score 47

---

### Module 06 — Human-Agent Dependency Map
**File:** `modules/human_agent_map.py`
**Route:** `GET /api/human-agent-map`

**Kya karta hai:**
- Har insaan ka ownership tree banata hai
- Coverage score calculate karta hai
- Human SPOFs identify karta hai (3+ agents with no backup)
- Coverage gaps list karta hai

**Sunrise Care Findings:**
- **Robert = Human SPOF** — 5 agents, 0% coverage
- Sarah = 100% coverage
- 9 coverage gaps

---

### Module 07 — AI Tool Intelligence
**File:** `modules/ai_tool_intelligence.py`
**Route:** `GET /api/tools`, `GET /api/tool-intelligence`, `GET /api/tool-impact`

**Kya karta hai:**
- Har AI tool ko risk score karta hai
- Tool-to-agent aur tool-to-workflow dependencies map karta hai
- Department-level exposure dikhata hai
- Monthly AI tool spend calculate karta hai

**Sunrise Care Findings:**
- ChatGPT = CRITICAL — 7 users, 4 departments
- Monthly spend: $1,444

---

### Module 08 — Workflow Intelligence
**File:** `modules/workflow_intelligence.py`
**Route:** `GET /api/workflows`

**Kya karta hai:**
- Har workflow ko step-by-step map karta hai
- Risk score karta hai ownership gaps, documentation, SPOF ke basis pe
- Single-node failure points identify karta hai

**Sunrise Care Findings:**
- 2 CRITICAL workflows
- 14 single-node failure points
- 3 workflows undocumented

---

### Module 09 — Knowledge Risk Intelligence
**File:** `modules/knowledge_risk_intelligence.py`
**Route:** `GET /api/knowledge/intelligence`, `GET /api/knowledge/impact`, `GET /api/knowledge/gaps`

**Kya karta hai:**
- Knowledge Concentration Score calculate karta hai
- Sole knowledge holders dhundhta hai
- Undocumented assets list karta hai
- Knowledge gaps identify karta hai

**Sunrise Care Findings:**
- Robert = 100% knowledge concentration
- 13 undocumented assets
- 15 knowledge gaps

---

### Module 10 — Organizational Memory Intelligence
**File:** `modules/organizational_memory_intelligence.py`
**Route:** `GET /api/memory`

**Kya karta hai:**
- Har asset ki memory status assign karta hai: PRESERVED / AT RISK / VULNERABLE / LOST
- Institutional Memory Health Score calculate karta hai
- Critical memory carriers identify karta hai

**Memory Status:**
| Status | Matlab |
|--------|--------|
| PRESERVED | Documented + backup hai |
| AT RISK | Backup hai lekin documentation nahi |
| VULNERABLE | Documentation hai lekin backup nahi |
| LOST | Na owner, na documentation — unrecoverable |

**Sunrise Care Findings:**
- PRESERVED: 14 · VULNERABLE: 10 · AT RISK: 1 · LOST: 2
- **Health Score: 54/100 — AT RISK**

---

## 8. Phase 2 — Platform Foundation

### Intelligence Pipeline
**File:** `modules/intelligence_pipeline.py`

Cross-pillar intelligence layer jo sab data sources ko ek unified graph mein connect karta hai. Entities, policies, aur links build karta hai.

### Data Models
**File:** `modules/data_models.py`

Core data structures:
- **Entity** — koi bhi asset
- **GovernancePolicy** — policies
- **AccountabilityLink** — RACI chain
- **GovernanceGap** — governance weaknesses
- **PillarResult** — pillar health metrics

### Storage Layer
**File:** `modules/storage_layer.py`

Analysis results ko JSON mein save karta hai with timestamps.

### Governance Data Framework
**File:** `modules/governance_data_framework.py`

Governance scoring aur gap detection ka engine. Har entity ko 0-100 score karta hai.

---

## 9. Phase 3 — Governance & Accountability

### Module 19 — Governance Intelligence
**File:** `modules/governance_intelligence.py`
**Route:** `GET /api/governance/intelligence`

**Sawaal jawab karta hai:** "Kaun kya own karta hai? Governance kaam kar raha hai? Kamzori kahan hai?"

**Kya karta hai:**
- Har entity ka Governance Score (0-100)
- Entities ko classify karta hai: HEALTHY / WARNING / AT RISK / CRITICAL
- Department-wise heatmap banata hai
- Governance risks detect karta hai

**Scoring:**
- No owner → -40
- Not documented → -20
- No policy → -25
- Expired policy → -15
- No enforcement → -10
- High-criticality with zero coverage → -15

**Sunrise Care:** Score 70/100 — WARNING

---

### Module 20 — Accountability Intelligence
**File:** `modules/accountability_intelligence.py`
**Route:** `GET /api/accountability/intelligence`

**Sawaal jawab karta hai:** "Ye kis ne approve kiya? Kaun responsible hai? Kaun accountable hai?"

**Kya karta hai:**
- RACI-style analysis (Responsible, Accountable, Consulted, Informed)
- Accountability Score (0-100)
- Separation-of-duties violations
- Responsibility Chains
- Decision Ownership mapping

**Scoring:**
- No responsible → -30
- No accountable → -25
- Same person responsible AND accountable → -10
- No consultation → -10
- No informed parties → -5
- No decision authority → -15

**Sunrise Care:** Score 76/100 — WARNING

---

## 10. Phase 4 — Executive Avatar & Voice Intelligence

### Module 21 — Executive Avatar Intelligence
**File:** `modules/executive_avatar_intelligence.py`
**Route:** `POST /api/avatar/intelligence/query`

**Kya karta hai:**
- Natural language queries process karta hai
- Intent detect karta hai (8 types)
- Entities resolve karta hai
- Contextual responses generate karta hai

**Code Flow:**
```python
# Query aata hai
query = "Robert chala jaye to kya hoga?"

# Intent detect hota hai
intent = detect_intent(query)  # "simulation"

# Entities resolve hote hain
entities = extract_entities(query, context)  # ["Robert"]

# Response generate hota hai
response = generate_response(query, intent, entities, context)
# "If Robert leaves: 5 agents affected, 5 coverage gaps."
```

**Sunrise Care:** 8 queries processed, 0.55 avg confidence, 6 intents detected

---

### Module 22 — Voice Intelligence Engine
**File:** `modules/voice_intelligence.py`

**Kya karta hai:**
- Voice commands parse karta hai
- 8 intent patterns against check karta hai
- Voice-appropriate responses generate karta hai
- Confidence scoring

**Voice Commands:**
1. `query_risk` — "What are the risks?"
2. `query_owner` — "Who owns this?"
3. `query_health` — "How healthy are we?"
4. `query_dependencies` — "What depends on this?"
5. `simulate_departure` — "What if someone leaves?"
6. `recommend_action` — "What should we fix?"
7. `list_assets` — "Show me all agents"
8. `compare_entities` — "Compare Robert and Lisa"

**Sunrise Care:** 10 commands, 0.73 avg confidence, 80% entity resolution

---

### Module 23 — Executive Briefing Intelligence
**File:** `modules/executive_briefing_intelligence.py`
**Route:** `GET /api/briefing/intelligence`

**Kya karta hai:**
- Automated executive briefings generate karta hai
- Sections: Asset Risk, Documentation Gaps, Human SPOFs, Governance
- Key metrics calculate karta hai
- Prioritized recommended actions deta hai

**Output:**
- Executive Summary
- Key Metrics Table
- Briefing Sections with priority
- Top 4 Recommended Actions
- Health Trajectory

---

### Module 27 — Executive Context Intelligence
**File:** `modules/executive_context_intelligence.py`

**Kya karta hai:**
- Context packages pre-compute karta hai
- Entity context, person context, organization summary
- Relevance scores assign karta hai
- Instant retrieval ke liye ready karta hai

---

## 11. Phase 5 — Organizational Scale Intelligence

### Module 28 — Universal Dependency Graph
**File:** `modules/universal_dependency_graph.py`
**Route:** `GET /api/universal-dep/intelligence`

**Module 02 ka evolved version.** Ab sirf agents nahi, poora organization map karta hai.

**Kya karta hai:**
- Har entity ko graph mein map karta hai
- SPOFs detect karta hai (humans, policies, tools sab)
- Cascade depth calculate karta hai
- Cascade chains trace karta hai

**Sunrise Care:** 43 nodes, 115 edges, 12 SPOFs, max cascade depth 5

---

### Module 29 — Organizational Relationship Intelligence
**File:** `modules/org_relationship_intelligence.py`

**Module 01 ka evolved version.** Relationships ki health samajhta hai.

**Kya karta hai:**
- Har relationship type ki health score
- Weak connections (degree ≤ 1)
- Strong connections (degree ≥ 7)
- Overall relationship health

---

### Module 31 — Organizational Ecosystem Intelligence
**File:** `modules/ecosystem_intelligence.py`

**Module 07 ka evolved version.** Poora ecosystem map karta hai.

**Kya karta hai:**
- Har entity ko ecosystem actor ke roop mein map karta hai
- Department coverage
- Tool adoption metrics
- Ecosystem health

---

### Module 34 — Hidden Dependency Intelligence
**File:** `modules/hidden_dependency_intelligence.py`

**Module 02 ka evolved version.** Chhupi hui dependencies dhundhta hai.

**Kya karta hai:**
- Shared-owner dependencies detect karta hai
- Shared-tool dependencies detect karta hai
- Risk level assign karta hai (HIGH/MEDIUM)

**Sunrise Care:** 11 hidden dependencies, 10 HIGH, 1 MEDIUM

---

### Module 35 — Organizational Network Intelligence
**File:** `modules/network_intelligence.py`
**Route:** `GET /api/network/intelligence`

**Module 08 ka evolved version.** Network behavior samajhta hai.

**Kya karta hai:**
- Centrality metrics (degree, betweenness, closeness)
- Network roles identify karta hai (hub, bridge, connector, peripheral)
- Clusters detect karta hai
- Influencers aur isolates dhundhta hai
- Network density aur centralization

**Sunrise Care:** 43 nodes, avg degree 5.35, 5 influencers, 3 isolates

---

## 12. Backend API Routes

### Phase 1 Routes:
| Endpoint | Module | Kya karta hai |
|----------|--------|---------------|
| `GET /api/agents` | 01 | Sab agents with ownership |
| `GET /api/ownership` | 01 | Owners mapped to agents |
| `GET /api/dependencies` | 02 | Dependency graph |
| `GET /api/risks` | 03 | Risk breakdown |
| `GET /api/dashboard` | 03 | Executive summary |
| `GET /api/human-agent-map` | 06 | Person → agents |
| `GET /api/tools` | 07 | AI tools |
| `GET /api/tool-intelligence` | 07 | Tool risk analysis |
| `GET /api/tool-impact` | 07 | Tool failure impact |
| `GET /api/workflows` | 08 | Workflows |
| `GET /api/knowledge/intelligence` | 09 | Knowledge scores |
| `GET /api/knowledge/impact` | 09 | Asset loss mapping |
| `GET /api/knowledge/gaps` | 09 | Undocumented assets |
| `GET /api/memory` | 10 | Memory status |
| `GET /api/simulations/employee-leaves` | 05 | Person leaving impact |
| `GET /api/simulations/agent-fails` | 05 | Agent failure impact |
| `GET /api/simulations/platform-down` | 05 | Tool offline impact |
| `GET /api/simulations/workflow-disruption` | 05 | Workflow break impact |

### Phase 2-3 Routes:
| Endpoint | Module | Kya karta hai |
|----------|--------|---------------|
| `GET /api/governance/intelligence` | 19 | Governance score, heatmap |
| `GET /api/accountability/intelligence` | 20 | Accountability, RACI |

### Architecture Layer Routes:
| Endpoint | Layer | Kya karta hai |
|----------|-------|---------------|
| `GET /api/ontology/intelligence` | Ontology | Entity types, relationships |
| `GET /api/ontology/entities` | Ontology | Entities with filtering |
| `GET /api/ontology/entities/:id` | Ontology | Single entity + relationships |
| `GET /api/ontology/relationships` | Ontology | Relationships with filtering |
| `GET /api/ontology/types` | Ontology | Type definitions |
| `GET /api/relationship/intelligence` | Relationship | Graph traversal, centrality |
| `GET /api/relationship/paths` | Relationship | Paths between entities |
| `GET /api/context/intelligence` | Context | Context packages |
| `GET /api/context/voice` | Voice | Voice models, intents |

### Phase 4 Routes:
| Endpoint | Module | Kya karta hai |
|----------|--------|---------------|
| `POST /api/avatar/intelligence/query` | M21 | Natural language query |
| `POST /api/avatar/intelligence/batch` | M21 | Batch queries |
| `GET /api/briefing/intelligence` | M23 | Executive briefing |
| `GET /api/briefing/intelligence/entity/:id` | M23 | Entity briefing |

### Phase 5 Routes:
| Endpoint | Module | Kya karta hai |
|----------|--------|---------------|
| `GET /api/universal-dep/intelligence` | M28 | Universal dependency graph |
| `GET /api/network/intelligence` | M35 | Network intelligence |

---

## 13. Kaise Chalayein

### Step 1: Dependencies Install Karo

```bash
# Python dependencies
uv sync

# Backend dependencies
cd backend
npm install

# Frontend dependencies
cd ../frontend
npm install
```

### Step 2: Environment Setup Karo

```bash
cp backend/.env.example backend/.env
```

`.env` file mein apni Supabase credentials daalo:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_secret_key
PORT=3000
```

### Step 3: Python Engine Chalao

```bash
# Root directory se
uv run main.py
```

Ye sab 27 modules sequence mein chalayega aur terminal mein full analysis print karega.

### Step 4: Backend Server Chalao

```bash
cd backend
node index.js
```

Server start hoga `http://localhost:3000` pe.

### Step 5: Frontend Dashboard Chalao

```bash
cd frontend
npm run dev
```

Dashboard start hoga `http://localhost:3001` pe.

---

## Summary

| Phase | Modules | Total |
|-------|---------|-------|
| Phase 1 | M01-M10 | 10 |
| Phase 2 | Platform Foundation | 4 |
| Phase 3 | M19, M20 | 2 |
| Architecture Layers | Ontology, Relationship, Context, Voice | 4 |
| Phase 4 | M21, M22, M23, M27 | 4 |
| Phase 5 | M28, M29, M31, M34, M35 | 5 |
| **Total** | | **27+** |

**OBA Core = 27 modules + 4 architecture layers + 36 API endpoints = Complete Organizational Intelligence Platform**

---

***Horquva Engineering · 2026***
