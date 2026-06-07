# OBA Core — AI Workforce Intelligence
**Horquva | MVP Demo — Sunrise Care (Fictional Company)**

OBA (Organizational Brain Analysis) is the intelligence engine that discovers, maps, and analyzes AI agents inside an organization — finding who owns them, how they connect, what breaks if something goes wrong, and exactly what to do about it.

> **"The only thing that matters: This is actually useful."** — Horquva

---

## The Problem

Modern organizations are deploying AI agents faster than they can manage them. Nobody knows:
- Who owns which agent?
- What breaks if one agent fails?
- How severe is the risk if a key person leaves?

OBA Core answers all of this — automatically.

---

## Modules Implemented
### Module 01 — Ownership Intelligence
![Module 01 Output](Images/module_01.png)

Analyzes every AI agent to determine ownership status and risk.

**What it does:**
- Identifies the owner and backup owner of each agent
- Detects orphaned agents (no owner assigned)
- Flags owner concentration risk (one person owning too many agents)
- Calculates a risk level per agent: `LOW / MEDIUM / HIGH / CRITICAL`

**Risk scoring factors:**
- No owner → +40 points
- No backup owner → +30 points
- Not documented → +15 points
- Agent criticality (critical/high/medium/low) → up to +15 points

**Key findings on Sunrise Care demo:**
- Robert owns 5 agents with zero backups — highest single-owner risk
- 2 agents fully orphaned: Inventory Agent, Data Backup Agent
- 9 of 15 agents have no backup owner

---

### Module 02 — Dependency Intelligence 
Maps how agents depend on each other and simulates cascade failures.

**What it does:**
- Builds a full dependency graph (who feeds into whom)
- Detects Single Points of Failure (SPOF)
- Simulates cascade failures: if Agent X fails, which agents break?
- Shows upstream depth (how deep in a chain an agent sits)

**Key findings on Sunrise Care demo:**
- 4 Single Points of Failure identified
- 6 agents have 3+ downstream cascade victims
- If Onboarding Agent fails → 4 agents break
- If Inventory Agent fails → 4 agents break

---

### Module 03 — Risk Intelligence 
Fuses ownership risk and dependency risk into one final risk score per agent and computes an overall Organizational Health Score.

**What it does:**
- Combines Module 01 + Module 02 outputs into a single risk score per agent
- Applies risk tiers: `LOW / MEDIUM / HIGH / CRITICAL`
- CRITICAL rule: orphaned agent OR (SPOF + no backup owner)
- Calculates Organizational Health Score (0–100, lower = more dangerous)
- Shows detailed risk breakdown for every CRITICAL agent

**Key findings on Sunrise Care demo:**
- 5 agents at CRITICAL risk
- 6 agents at HIGH risk
- Organizational Health Score: **56/100 — AT RISK**

---

### Module 04 — Recommendation Engine
Generates specific, prioritized, actionable recommendations based on the risk analysis.

**What it does:**
- Reads Module 03 risk output for every agent
- Generates targeted actions for every CRITICAL and HIGH risk agent
- Prioritizes recommendations: CRITICAL first, then HIGH, then MEDIUM
- Produces a Top 5 Most Urgent Actions list
- Ends with a complete Demo Summary for stakeholder presentation

**Key findings on Sunrise Care demo:**
- 12 actionable recommendations generated
- Top priority: assign owners to orphaned agents immediately
- Redistribute Robert's 5 agents to eliminate single-owner dependency
- Organizational Health Score: 56/100 — recovery plan provided

---

## Demo Results 
## Terminal Output

### Demo Summary
![Demo Summary](Images/WhatTAha.png)
| Metric | Result |
|--------|--------|
| Total Agents Analyzed | 15 |
| CRITICAL Risk Agents | 5 |
| HIGH Risk Agents | 6 |
| Single Points of Failure | 4 |
| Robert's Agents (zero backups) | 5 → CRITICAL |
| If Robert Leaves | 5 agents immediately unmanaged |
| Organizational Health Score | 56/100 — AT RISK |
| Recommendations Generated | 12 |

---

## Dataset

`data/sunrise_care.json` — fictional company (Sunrise Care) with:
- 120 employees
- 15 AI agents across Sales, Finance, HR, Operations, Support, Marketing
- 14 dependency relationships
- 3 primary owners: Robert, Sarah, Lisa
- 2 fully unowned (orphaned) agents
- Designed to stress-test: Robert owns 5 agents, no backups, 3 critical dependencies

---

## Project Structure
data/
sunrise_care.json               # agent + dependency dataset
modules/
init.py
ownership_intelligence.py       # Module 01 — Huzaifa
dependency_intelligence.py      # Module 02 — Huzaifa
risk_intelligence.py            # Module 03 — Kamran
recommendation_engine.py        # Module 04 — Kamran
main.py                           # runs all 4 modules
pyproject.toml                    # dependencies
uv.lock                           # locked dependency versions

---

## How to Run

```bash
# Install dependencies
uv sync

# Run all 4 modules
uv run main.py
```

> This project uses [uv](https://github.com/astral-sh/uv) as the package manager.  
> All dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

---

## Tech Stack

| What | Tool |
|------|------|
| AI Logic | Python |
| Package Manager | uv |
| Terminal Output | rich |
| Dataset | JSON |
| Version Control | GitHub |

---

## Team

| Module | Engineer |
|--------|----------|
| Module 01 — Ownership Intelligence | Huzaifa |
| Module 02 — Dependency Intelligence | Huzaifa |
| Module 03 — Risk Intelligence | Kamran |
| Module 04 — Recommendation Engine | Kamran |