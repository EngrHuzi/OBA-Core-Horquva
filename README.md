# OBA Core — AI Workforce Intelligence Engine

**Developed by Horquva · MVP Demo · Sunrise Care (Fictional Company)**

OBA Core (Organizational Brain Analysis) is an enterprise-grade intelligence engine that automatically discovers, maps, and analyzes every AI agent operating inside an organization. It answers the three questions no organization can currently answer:

- **Who owns each AI agent?**
- **What breaks — and how badly — if one fails?**
- **What happens to the organization if a key person leaves?**

OBA Core answers all of this in seconds, with full risk scoring, cascade simulation, and prioritized action plans.

![OBA Core Executive Dashboard](Images/dashboard.png)
> [!IMPORTANT]
> # **"The only thing that matters: This is actually useful." — Horquva**





---

## The Problem We Solve

Organizations are deploying AI agents faster than they can govern them. The result is invisible risk:

- Agents running with no owner, no documentation, no backup
- One person quietly controlling 5+ critical agents — with zero coverage
- Nobody knowing which agent failure cascades into a full department breakdown
- Leadership making decisions with no visibility into their AI infrastructure

**OBA Core makes the invisible visible.**

---

## What Was Built

OBA Core is a full-stack intelligence platform with three layers:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Intelligence Engine | Python · uv · rich | 10 analytical modules that process org data |
| Backend API | Node.js · Express · Supabase | REST API serving all intelligence data |
| Executive Dashboard | Next.js 16 · TypeScript · Tailwind · Recharts | Interactive visualization for leadership |

---

## Intelligence Modules (10 Total)

### Module 01 — Ownership Intelligence
![Module 01 Output](Images/agent_summary.png)

Analyzes every AI agent across the organization and scores ownership risk.

**What it does:**
- Identifies the primary owner and backup owner for each agent
- Detects fully orphaned agents (no owner assigned whatsoever)
- Flags owner concentration risk — one person controlling too many critical agents
- Calculates a risk level per agent: `LOW / MEDIUM / HIGH / CRITICAL`

**Risk Scoring Formula:**
| Factor | Points Added |
|--------|-------------|
| No owner assigned | +40 |
| No backup owner | +30 |
| Not documented | +15 |
| Agent criticality: critical | +15 |
| Agent criticality: high | +10 |
| Agent criticality: medium | +5 |

**Score → Risk Tier:** `< 20 = LOW` · `20–39 = MEDIUM` · `40–69 = HIGH` · `70+ = CRITICAL`

**Sunrise Care findings:**
- Robert owns 5 agents — zero backups — highest single-owner concentration in the org
- 2 agents fully orphaned: Inventory Agent, Data Backup Agent
- 9 of 15 agents have no backup owner

---

### Module 02 — Dependency Intelligence
![Module 02 Output](Images/dependency_map.png)

Builds a full dependency graph of all AI agents and maps cascade failure paths.

**What it does:**
- Constructs a directed dependency graph: which agents feed into which
- Detects Single Points of Failure (SPOF) — agents whose failure breaks 3+ downstream agents
- Simulates cascade failure: if Agent X goes down, which agents are affected?
- Calculates upstream depth — how deep in a dependency chain each agent sits

**Sunrise Care findings:**
- 4 Single Points of Failure identified across 15 agents
- 6 agents have 3 or more downstream cascade victims
- Onboarding Agent failure → 4 agents immediately break
- Inventory Agent failure → 4 agents immediately break

---

### Module 03 — Risk Intelligence
![Module 03 Output](Images/riskanalysis.png)

Fuses ownership risk and dependency data into a single composite risk score per agent, then computes the Organizational Health Score.

**What it does:**
- Combines Module 01 + Module 02 outputs into one unified risk score
- Applies CRITICAL override rule: any orphaned agent OR any SPOF with no backup = CRITICAL regardless of score
- Calculates the **Organizational Health Score (0–100)** — a single number representing how well-governed the organization's AI infrastructure is
- Produces a complete risk breakdown per agent for executive review

**Sunrise Care findings:**
- 5 agents at CRITICAL risk
- 6 agents at HIGH risk
- **Organizational Health Score: 56/100 — AT RISK**

---

### Module 04 — Recommendation Engine
![Module 04 Output](Images/recommendations1.png)

Generates specific, named, prioritized actions based on every risk finding — not generic advice.

**What it does:**
- Reads every risk finding from Module 03 for every agent
- Generates a targeted recommendation per risk: names the agent, names the person, names the exact action
- Prioritizes all recommendations: CRITICAL → HIGH → MEDIUM, then Quick wins first
- Produces a Top 5 Most Urgent Actions list for immediate leadership action
- Calculates how each fix improves the Organizational Health Score

**Sunrise Care findings:**
- 12 actionable recommendations generated
- Top priority: immediately assign owners to Inventory Agent and Data Backup Agent
- Redistribute Robert's 5 agents — single departure would orphan all of them
- Recovery plan provided with projected Health Score improvement per action

---

### Module 05 — What-If Simulation Engine
![Module 05 Output](Images/what_ifl.png)

Simulates every possible disruption scenario and calculates its exact impact on organizational health before it happens.

**What it does:**
- Simulates every owner leaving the organization (one by one)
- Simulates every CRITICAL/HIGH/SPOF agent failing
- Recalculates the Organizational Health Score for each scenario in real time
- Shows before → after risk level for every affected agent
- Ranks all scenarios from most dangerous to least — so leadership knows exactly where fragility lives

**Simulation logic:**
- **Person Leaves** → their agents lose primary ownership (+35 risk each), Health Score recalculated
- **Agent Fails** → failed agent reaches maximum risk (score 170), all cascade victims receive +30 risk penalty

**Sunrise Care findings:**
- **Worst scenario: Robert leaves → Health Score collapses from 56 → 49**
- 5 agents become immediately unmanaged if Robert is unavailable
- Worst agent scenario: Onboarding Agent failure drops Health Score to 47
- Every scenario ranked so leadership can prioritize risk mitigation investment

---

### Module 06 — Human-Agent Dependency Map
![Module 06 Output](Images/ai_human_mapping.png)

Maps every person in the organization to the agents they control and scores human-level coverage risk.

**What it does:**
- Builds a complete ownership tree per person: which agents they own, at what risk level
- Calculates a coverage score per person: what % of their agents have backup owners
- Identifies Human SPOFs: individuals who own 3+ agents with no backup coverage anywhere
- Lists every coverage gap across the organization with exact agent names

![Human-Agent Map Summary](Images/Human_map_summary.png)

**Sunrise Care findings:**
- **Robert = Human SPOF** — 5 agents owned, 0% coverage, all CRITICAL or HIGH risk
- Sarah = 100% coverage — all 3 of her agents have backup owners
- 9 total coverage gaps identified across the organization
- 7 agents have a primary owner but zero backup coverage

---

### Module 07 — AI Tool Intelligence
![Module 07 Output](Images/Module_07.png)

Audits every AI tool in use across the organization — usage, risk, dependencies, and financial exposure.

**What it does:**

![](Images/Module_07(1).png)

- Scores every AI tool for risk: ChatGPT, Claude, Gemini, Microsoft Copilot, GitHub Copilot
- Maps tool-to-agent and tool-to-workflow dependencies: if this tool goes offline, what breaks?
- Identifies tools with no backup/alternative and no usage policy
- Shows department-level exposure per tool
- Calculates total monthly AI tool spend across the organization

**Sunrise Care findings:**
- ChatGPT = CRITICAL — 7 users, 4 departments, powers 3 agents, no policy, no backup
- Microsoft Copilot = HIGH — 8 users across all 8 departments, no backup alternative
- 3 of 5 tools have no fallback option assigned
- If ChatGPT access is revoked: Lead Generation, Marketing Campaign, and Customer Support workflows all break simultaneously
- **Total monthly AI tool spend: $1,444**

---

### Module 08 — Workflow Intelligence
![Module 08 Output](Images/Module_08.png)

Maps every business workflow step by step — Human → Tool → Agent → Outcome — and scores failure risk at each node.

**What it does:**
- Visualizes every workflow as a full sequential chain with named actors at each step
- Scores each workflow for risk: ownership gaps, undocumented status, human SPOF dependency
- Identifies single-node failure points — the one person or tool whose removal collapses the entire workflow
- Surfaces workflows with no runbook, no backup owner, and no recovery path

**Sunrise Care findings:**
- 2 CRITICAL workflows: Lead Generation (Robert, no backup, undocumented) and IT Operations (David, no backup, undocumented)
- All 7 workflows have exactly one human dependency — no workflow survives its owner leaving
- 14 single-node failure points identified across all workflows
- 3 workflows have zero documentation: Lead Generation, IT Operations, Analytics Reporting

---

### Module 09 — Knowledge Risk Intelligence
![Module 09 Output](Images/Module_09.png)

Maps where critical organizational knowledge is stored — in people's heads — and calculates what disappears if they leave.

**What it does:**

![](Images/Module_09(1).png)

- Calculates a Knowledge Concentration Score per person (0–100%)
- Identifies sole knowledge holders: people who are the only ones who know how a critical asset works
- Lists every undocumented agent, workflow, and AI tool across the organization
- Maps exactly which assets are unrecoverable if a specific person leaves today
- Surfaces knowledge gaps: assets with no documentation AND no backup owner

**Sunrise Care findings:**
- Robert = CRITICAL knowledge concentration (100%) — sole owner of 5 agents + 1 workflow, all undocumented
- Mike and Lisa = HIGH concentration risk (64% and 54%)
- 13 total undocumented assets across agents, workflows, and tools
- If Robert leaves today: 6 assets are permanently unrecoverable with no documentation and no backup

---

### Module 10 — Organizational Memory Intelligence
![Module 10 Output](Images/Module_10.png)

Tracks the institutional memory preservation status of every AI asset and calculates how much organizational knowledge would survive a major personnel disruption.

**What it does:**
- Assigns a memory status to every asset: `PRESERVED / AT RISK / VULNERABLE / LOST`
- Calculates the **Institutional Memory Health Score™ (0–100)**
- Identifies critical memory carriers — individuals who are the sole holders of undocumented knowledge
- Flags assets classified as LOST: no owner, no documentation, no recovery path

**Memory Status Definitions:**
| Status | Meaning |
|--------|---------|
| PRESERVED | Documented + backup owner exists |
| AT RISK | Has backup but lacks documentation |
| VULNERABLE | Has documentation but no backup owner |
| LOST | No owner, no documentation — unrecoverable |

**Sunrise Care findings:**
- PRESERVED: 14 assets · VULNERABLE: 10 assets · AT RISK: 1 asset · LOST: 2 assets
- Robert = CRITICAL memory carrier — sole holder of 7 assets, 6 of which are undocumented
- David = HIGH risk — sole carrier of IT Operations Workflow + both IT tools, all undocumented
- **Institutional Memory Health Score: 54/100 — AT RISK**

---

## Demo Results Summary

![Demo Summary](Images/WhatTAha.png)

| Metric | Result |
|--------|--------|
| Total Agents Analyzed | 15 |
| CRITICAL Risk Agents | 5 |
| HIGH Risk Agents | 6 |
| Single Points of Failure (Agent) | 4 |
| Human Single Points of Failure | 1 (Robert) |
| Robert's Agents (zero backups) | 5 → all CRITICAL |
| Worst Scenario: Robert Leaves | Health Score: 56 → 49 |
| Organizational Health Score | **56/100 — AT RISK** |
| Institutional Memory Health Score | **54/100 — AT RISK** |
| Actionable Recommendations Generated | 12 |
| Total Coverage Gaps | 9 |
| Total Undocumented Assets | 13 |
| Total Knowledge Gaps | 15 |
| Total Monthly AI Tool Spend | $1,444 |

---

## Demo Dataset

**File:** `data/sunrise_care.json`

A purpose-built fictional company dataset engineered to stress-test all 10 modules simultaneously.

- 120 employees across 8 departments
- 15 AI agents: Sales, Finance, HR, Operations, Support, Marketing
- 14 agent dependency relationships
- 5 AI tools in active use
- 7 business workflows mapped end-to-end
- 3 primary owners: Robert (5 agents), Sarah (3 agents), Lisa (2 agents)
- 2 fully orphaned agents: Inventory Agent, Data Backup Agent
- Designed so Robert's departure triggers maximum cascade damage across the org

---

## How to Run

### 1 — Python Intelligence Engine

Runs all 10 modules in sequence and prints full analysis to the terminal.

```bash
# Install dependencies (requires uv)
uv sync

# Run all 10 modules
uv run main.py
```

> This project uses [uv](https://github.com/astral-sh/uv) as the Python package manager.
> All dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

---

### 2 — Backend API (Node.js + Express + Supabase)

```bash
cd backend

# Install dependencies
npm install

# Start the server
node index.js
```

Server starts on **`http://localhost:3000`**

#### All API Endpoints

| Endpoint | Module | Description |
|----------|--------|-------------|
| `GET /api/agents` | 01 | All agents with ownership, risk level, and metadata |
| `GET /api/ownership` | 01 | Owners mapped to their agents with risk scores |
| `GET /api/dependencies` | 02 | Full dependency graph with cascade relationships |
| `GET /api/risks` | 03 | Composite risk score breakdown per agent |
| `GET /api/dashboard` | 03 | Executive summary: health score, critical counts, orphan count |
| `GET /api/human-agent-map` | 06 | Person → agents ownership tree with coverage scores |
| `GET /api/tools` | 07 | All AI tools with user counts and risk levels |
| `GET /api/tool-intelligence` | 07 | Tool risk analysis with department exposure |
| `GET /api/tool-impact` | 07 | Impact simulation: what breaks if a tool goes offline |
| `GET /api/workflows` | 08 | All workflows with step chains and risk scores |
| `GET /api/knowledge/intelligence` | 09 | Knowledge concentration scores per person |
| `GET /api/knowledge/impact` | 09 | Asset loss mapping per person departure |
| `GET /api/knowledge/gaps` | 09 | All undocumented assets with no backup |
| `GET /api/memory` | 10 | Institutional memory status per asset |
| `GET /api/simulations/employee-leaves` | 05 | Health Score impact when a person leaves |
| `GET /api/simulations/agent-fails` | 05 | Health Score impact when an agent fails |
| `GET /api/simulations/platform-down` | 05 | Health Score impact when a tool goes offline |
| `GET /api/simulations/workflow-disruption` | 05 | Health Score impact when a workflow breaks |

#### Environment Setup

```bash
# Copy the template
cp backend/.env.example backend/.env
```

Fill in your Supabase credentials in `backend/.env`:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_secret_key
PORT=3000
```

> `.env` is git-ignored and must never be committed to version control.

---

### 3 — Executive Frontend Dashboard

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Dashboard runs on **`http://localhost:3001`**

Also accessible on your local network at **`http://<your-ip>:3001`**

---

## Project Structure

```
OBA-Core-Horquva/
│
├── data/
│   └── sunrise_care.json                      # Demo dataset (120 employees, 15 agents)
│
├── modules/
│   ├── __init__.py
│   ├── ownership_intelligence.py              # Module 01 — Ownership Analysis
│   ├── dependency_intelligence.py             # Module 02 — Dependency Mapping
│   ├── risk_intelligence.py                   # Module 03 — Risk Scoring
│   ├── recommendation_engine.py               # Module 04 — Action Recommendations
│   ├── whatif_simulation.py                   # Module 05 — What-If Simulation
│   ├── human_agent_map.py                     # Module 06 — Human-Agent Map
│   ├── ai_tool_intelligence.py                # Module 07 — AI Tool Intelligence
│   ├── workflow_intelligence.py               # Module 08 — Workflow Intelligence
│   ├── knowledge_risk_intelligence.py         # Module 09 — Knowledge Risk
│   └── organizational_memory_intelligence.py  # Module 10 — Organizational Memory
│
├── backend/
│   ├── index.js                               # Express server — all routes registered here
│   ├── supabase.js                            # Supabase client initialization
│   ├── package.json                           # Node.js dependencies
│   ├── .env.example                           # Environment variable template
│   └── routes/
│       ├── agents.js                          # /api/agents
│       ├── ownership.js                       # /api/ownership
│       ├── dependencies.js                    # /api/dependencies
│       ├── risks.js                           # /api/risks
│       ├── dashboard.js                       # /api/dashboard
│       ├── humanAgentMap.js                   # /api/human-agent-map
│       ├── tools.js                           # /api/tools
│       ├── toolIntelligence.js                # /api/tool-intelligence
│       ├── toolImpact.js                      # /api/tool-impact
│       ├── simulations/
│       │   ├── employeeLeaves.js              # /api/simulations/employee-leaves
│       │   ├── agentFails.js                  # /api/simulations/agent-fails
│       │   ├── platformDown.js                # /api/simulations/platform-down
│       │   └── workflowDisruption.js          # /api/simulations/workflow-disruption
│       ├── workflows/
│       │   ├── index.js                       # /api/workflows
│       │   ├── intelligence.js
│       │   ├── failures.js
│       │   └── spof.js
│       ├── knowledge/
│       │   ├── intelligence.js                # /api/knowledge/intelligence
│       │   ├── impact.js                      # /api/knowledge/impact
│       │   └── gaps.js                        # /api/knowledge/gaps
│       └── memory/
│           └── memory.js                      # /api/memory
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                         # Shell: persistent sidebar navigation
│   │   ├── globals.css                        # Design system, tokens, dark theme
│   │   ├── page.tsx                           # Screen 1: Executive Dashboard
│   │   ├── ownership/page.tsx                 # Screen 2: Ownership Intelligence
│   │   ├── risk/page.tsx                      # Screen 3: Risk Intelligence
│   │   ├── map/page.tsx                       # Screen 4: Dependency Map
│   │   ├── simulation/page.tsx                # Screen 5: What-If Simulation
│   │   └── recommendations/page.tsx           # Screen 6: Recommendations
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx                    # Navigation sidebar (6 routes)
│   │   │   └── Topbar.tsx                     # Top navigation bar
│   │   ├── dashboard/
│   │   │   ├── KpiStrip.tsx                   # Key metrics strip
│   │   │   ├── Heatmap.tsx                    # Agent risk heatmap
│   │   │   ├── RiskSplit.tsx                  # Risk tier distribution chart
│   │   │   └── AgentTable.tsx                 # Full agent data table
│   │   ├── ownership/
│   │   │   ├── OwnershipOverview.tsx          # Ownership summary panel
│   │   │   ├── ConcentrationBar.tsx           # Owner concentration bar chart
│   │   │   ├── OwnershipList.tsx              # Per-owner agent list
│   │   │   ├── HumanDependencyRisks.tsx       # Human SPOF indicators
│   │   │   ├── DependencyPipeline.tsx         # Dependency pipeline view
│   │   │   └── OrgRelationshipMap.tsx         # Org-level relationship map
│   │   ├── risk/
│   │   │   ├── RiskHeader.tsx                 # Risk page header with health score
│   │   │   ├── OrgHealthBanner.tsx            # Org Health Score banner
│   │   │   ├── CriticalRiskPanel.tsx          # CRITICAL agents panel
│   │   │   └── RiskScoreTable.tsx             # Full risk score table
│   │   ├── map/
│   │   │   ├── FlowCanvas.tsx                 # Interactive dependency flow diagram
│   │   │   ├── CustomNodes.tsx                # Custom node renderers
│   │   │   ├── DependencyKPIs.tsx             # Dependency KPI cards
│   │   │   └── DependencyTable.tsx            # Dependency data table
│   │   ├── simulation/
│   │   │   ├── SimulationDashboard.tsx        # Simulation control panel
│   │   │   ├── ScenarioRanking.tsx            # Scenarios ranked by impact
│   │   │   └── ImpactSummary.tsx              # Before/after impact summary
│   │   └── recommendations/
│   │       ├── RecommendationHeader.tsx       # Recommendations page header
│   │       ├── Top5Urgent.tsx                 # Top 5 urgent actions
│   │       ├── RecommendationList.tsx         # Full recommendations list
│   │       └── DemoSummary.tsx                # Final demo summary panel
│   ├── lib/
│   │   ├── data.ts                            # Server-side JSON data loader
│   │   ├── graph.ts                           # Graph traversal and cascade logic
│   │   ├── risk.ts                            # Risk scoring utilities
│   │   ├── simulation.ts                      # What-If scenario engine (TS)
│   │   └── recommendations.ts                 # Recommendation generation logic
│   └── types/
│       └── index.ts                           # TypeScript type definitions
│
├── Images/                                    # All module output screenshots
├── main.py                                    # Runs all 10 Python modules in sequence
├── pyproject.toml                             # Python project dependencies
└── uv.lock                                    # Locked Python dependency versions
```

---

## Full Tech Stack

| Layer | Component | Technology |
|-------|-----------|-----------|
| Intelligence Engine | Core Logic | Python 3.13 |
| Intelligence Engine | Package Manager | uv |
| Intelligence Engine | Terminal Output | rich |
| Intelligence Engine | Data Format | JSON |
| Backend | Server Framework | Node.js + Express 5 |
| Backend | Database | Supabase (PostgreSQL) |
| Backend | DB Client | @supabase/supabase-js |
| Backend | Environment | dotenv |
| Frontend | Framework | Next.js 16 (Turbopack) |
| Frontend | Language | TypeScript |
| Frontend | Styling | Tailwind CSS v4 |
| Frontend | Charts | Recharts |
| Frontend | Icons | Lucide React |
| Both | Version Control | GitHub |

---

## Module Engineering

| Module | Name | Lead Engineer |
|--------|------|---------------|
| Module 01 | Ownership Intelligence | Huzaifa |
| Module 02 | Dependency Intelligence | Huzaifa |
| Module 03 | Risk Intelligence | Huzaifa |
| Module 04 | Recommendation Engine | Kamran |
| Module 05 | What-If Simulation Engine | Kamran |
| Module 06 | Human-Agent Dependency Map | Kamran |
| Module 07 | AI Tool Intelligence | Huzaifa |
| Module 08 | Workflow Intelligence | Huzaifa |
| Module 09 | Knowledge Risk Intelligence | Kamran |
| Module 10 | Organizational Memory Intelligence | Kamran |

---

***Built by Horquva Engineering · MVP Release · 2026***
