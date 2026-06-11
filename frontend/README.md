# Horquva Frontend — OBA Core Intelligence UI

**Next.js 16 · TypeScript · Tailwind CSS v4 · Recharts · Lucide Icons**

Executive-facing dashboard for the OBA (Organizational Brain Analysis) Core engine — visualizes AI workforce risk, ownership, and continuity intelligence across an organization using local JSON data.

---

## What's Built (Module 1 — Executive Dashboard)

### 01 Organizational Snapshot
Four KPI cards answering the executive's first question at a glance:
- **Platform Risk Score** — 72/100 with animated progress bar
- **Agents Found** — 15 active AI agents
- **Orphaned Agents** — 3 agents with no owner assigned
- **Critical Dependencies** — 5 high-impact agent connections

### 02 Risk Analysis
Full-width stacked bar chart showing **risk distribution by department** (Sales, Finance, HR, Operations, etc.) with Critical / High / Medium / Low tiers. Includes a grid background and custom legend below the chart.

### 03 Recommendations (Top Risks + Priority Actions)
Two-column split:
- **Left** — Top 5 critical agents requiring immediate attention, with owner status
- **Right** — Dynamically generated priority actions (assign owners, document workflows, review dependencies)

### 04 Agent Summary Directory
Complete agent registry table with 5 columns:
- **Agent Details** — name + department
- **Ownership** — primary + backup owner (flags orphaned and missing backup)
- **Documentation** — verified or missing
- **Criticality** — inherent business importance of the agent
- **Risk** — computed governance score (mirrors OBA Core Module 03 scoring: ownership + documentation + criticality weight)

### 05 Module 2 — Ownership Intelligence
- **Ownership Overview** — KPI strip for coverage gaps, SPOFs, and orphaned agents.
- **Concentration Bar** — Stacked bar mapping exposed vs covered agents per owner.
- **Ownership List** — Detailed registry of agents grouped by owner with specific risk badges.

### 06 Module 3 — Dependency Map
- **Dependency KPIs** — Strip showing Total Agents, Dependencies, SPOFs Detected, and Max Cascade Risk.
- **Dependency Flow Canvas** — React Flow node graph auto-layouted with Dagre, featuring interactive failure simulation and SPOF detection highlighting.
- **Agent Continuity Matrix** — An executive table summarizing upstream dependencies, downstream cascading impact, and continuity risk for each agent.

### 07 Module 4 — Continuity Intelligence (What-If Simulation)
- **Simulation Dashboard** — Coordinates baseline vs. simulated metrics.
- **Scenario Ranking** — Interactive list of scenarios (Person Leaves, Agent Fails) ranked by worst impact first.
- **Impact Summary** — Visually displays before/after Health Score and a detailed log of every impacted agent with their adjusted risk levels.

---

## Design System

- **Color palette** — near-black canvas (`#0c0c0f`) with elevated cards (`#16161c`)
- **Risk colors** — Critical (red) / High (orange) / Medium (yellow) / Low (green), all desaturated for readability
- **Typography** — DM Sans via `next/font/google`; HORQUVA wordmark uses Outfit 500
- **Animations** — staggered `fade-up` on page load, card hover lift (`translateY(-2px)`), icon scale, soft pulse on warning icons
- **Cards** — layered box-shadow for elevation, colored 2px top-border gradient per metric type, hover glow wash

---

## Screens (Route Stubs)

| Route | Status | Description |
|---|---|---|
| `/` | ✅ Built | Executive Dashboard (Module 1) |
| `/ownership` | ✅ Built | Ownership Intelligence (Module 2) |
| `/risk` | 🔜 Stub | Risk Intelligence |
| `/map` | ✅ Built | Dependency Map (Module 3) |
| `/simulation` | ✅ Built | What-If Simulation (Module 4) |
| `/recommendations` | 🔜 Stub | Recommendations (Module 5) |

---

## Data Source

All UI is powered by `../data/sunrise_care.json` (Sunrise Care demo dataset) loaded server-side via `lib/data.ts`. No API calls — pure local data for the MVP.

---

## Run Locally

```bash
cd frontend
npm install
npm run dev
```

Runs on **http://localhost:3001**

---

## Stack

| Layer | Tool |
|---|---|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS v4 |
| Charts | Recharts 3 |
| Icons | Lucide React |
| Graphs | React Flow (`@xyflow/react`) + Dagre |
| Data | Local JSON (`sunrise_care.json`) |
