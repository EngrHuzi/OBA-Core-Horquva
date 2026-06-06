# OBA Core — AI Workforce Intelligence

**Horquva** | MVP Demo - sunrise care (fictional company)

OBA (Organizational Brain Analysis) is the intelligence engine that discovers, maps, and analyzes AI agents inside an organization — finding who owns them, how they connect, and what breaks if something goes wrong.

---

## Modules Implemented

### Module 01 — Ownership Intelligence
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

**Key finding on sunrise care demo:**
- Robert owns 5 agents with zero backups — highest single-owner risk
- 2 agents are fully orphaned (no owner): Inventory Agent, Data Backup Agent
- 9 of 15 agents have no backup owner

---

### Module 02 — Dependency Intelligence
Maps how agents depend on each other and simulates cascade failures.

**What it does:**
- Builds a full dependency graph (who feeds into whom)
- Detects Single Points of Failure (SPOF) — agents with no upstream but many downstream dependents
- Simulates cascade failures: if Agent X fails, which agents break?
- Shows upstream depth (how deep in a chain an agent sits)

**Key finding on Sunrise care demo:**
- 4 Single Points of Failure identified
- 6 agents have 3+ downstream cascade victims
- If Onboarding Agent fails → 4 agents break (Payroll, Support Ticket, Customer Feedback, Report Generator)
- If Inventory Agent fails → 4 agents break (Scheduling, Appointment Reminder, CRM Sync, Billing)

---

## Dataset

`data/sunrise_care.json` — fictional company with:
- 120 employees
- 15 AI agents across Sales, Finance, HR, Operations, Support, Marketing
- 14 dependency relationships
- 3 primary owners (Robert, Sarah, Lisa) + 2 unowned agents

---

## Project Structure

```
data/
  sunrise_care.json          # agent + dependency dataset

modules/
  ownership_intelligence.py  # Module 01
  dependency_intelligence.py # Module 02

main.py                      # runs both modules
```

---

## How to Run

```bash
# Install dependencies
uv sync

# Run all modules
uv run main.py
```

> This project uses [uv](https://github.com/astral-sh/uv) as the package manager. All dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

---

## Tech Stack

| What | Tool |
|------|------|
| AI Logic | Python |
| Package Manager | uv |
| Output | rich |
| Dataset | JSON |
| Version Control | GitHub |
