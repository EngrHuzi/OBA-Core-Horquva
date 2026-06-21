import io
import json
import sys
from rich.console import Console

from modules.ownership_intelligence import run_ownership_intelligence, display_ownership_report
from modules.dependency_intelligence import run_dependency_intelligence, display_dependency_report
from modules.risk_intelligence import run_risk_intelligence, display_risk_report
from modules.recommendation_engine import generate_recommendations, display_recommendation_report
from modules.whatif_simulation import run_whatif_simulation, display_whatif_report
from modules.human_agent_map import run_human_agent_map, display_human_agent_map
from modules.ai_tool_intelligence import run_ai_tool_intelligence, display_ai_tool_report
from modules.workflow_intelligence import run_workflow_intelligence, display_workflow_report
<<<<<<< HEAD
from modules.knowledge_risk_intelligence import run_knowledge_risk_intelligence, display_knowledge_risk_report
from modules.organizational_memory_intelligence import run_organizational_memory_intelligence, display_organizational_memory_report
=======
from modules.governance_intelligence import run_governance_intelligence, display_governance_report
from modules.accountability_intelligence import run_accountability_intelligence, display_accountability_report
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)

DATA_PATH = "data/sunrise_care.json"


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    company = data["company"]
    console.print("\n=== OBA CORE — AI WORKFORCE INTELLIGENCE ===\n")

<<<<<<< HEAD
    # Module 01
=======
    # Phase 1 — Module 1
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    ownership_results = run_ownership_intelligence(DATA_PATH)
    display_ownership_report(ownership_results, company)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 02
=======
    # Phase 1 — Module 2
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    dependency_results = run_dependency_intelligence(DATA_PATH)
    display_dependency_report(dependency_results, data)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 03
=======
    # Phase 1 — Module 3
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    risk_results, health_score = run_risk_intelligence(DATA_PATH)
    display_risk_report(risk_results, health_score, company)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 04
=======
    # Phase 1 — Module 4
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    recommendations = generate_recommendations(risk_results, data)
    display_recommendation_report(recommendations, risk_results, health_score, company)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 05
=======
    # Phase 1 — Module 5
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    scenarios, baseline_health = run_whatif_simulation(DATA_PATH)
    display_whatif_report(scenarios, baseline_health, company)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 06
=======
    # Phase 1 — Module 6
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    profiles, gaps, results = run_human_agent_map(DATA_PATH)
    display_human_agent_map(profiles, gaps, results, company)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 07
=======
    # Phase 1 — Module 7
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    tool_risks, dep_maps, dept_tool_map = run_ai_tool_intelligence(DATA_PATH)
    display_ai_tool_report(tool_risks, dep_maps, dept_tool_map, company)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 08
=======
    # Phase 1 — Module 8
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))
    wf_risks, node_failures = run_workflow_intelligence(DATA_PATH)
    display_workflow_report(wf_risks, node_failures, company)
    console.print("\n" + "-" * 60 + "\n")

<<<<<<< HEAD
    # Module 09
    knowledge_nodes, knowledge_gaps, knowledge_summary = run_knowledge_risk_intelligence(DATA_PATH)
    display_knowledge_risk_report(knowledge_nodes, knowledge_gaps, knowledge_summary, company)
    console.print("\n" + "-" * 60 + "\n")

    # Module 10
    memory_nodes, memory_carriers, memory_health = run_organizational_memory_intelligence(DATA_PATH)
    display_organizational_memory_report(memory_nodes, memory_carriers, memory_health, company)

    console.print("\n=== OBA Core Analysis Complete — 10 Modules ===\n")
=======
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]PHASE 2 & 3 — GOVERNANCE & ACCOUNTABILITY PILLAR[/bold cyan]")
    console.print("=" * 60 + "\n")

    # Phase 3 — Module 19: Governance Intelligence
    gov_results, gov_score, gov_risks, dept_heatmap = run_governance_intelligence(DATA_PATH)
    display_governance_report(gov_results, gov_score, gov_risks, dept_heatmap, data["company"])

    console.print("\n" + "-" * 60 + "\n")

    # Phase 3 — Module 20: Accountability Intelligence
    acc_results, acc_score, chains, person_coverage = run_accountability_intelligence(DATA_PATH)
    display_accountability_report(acc_results, acc_score, chains, person_coverage, data["company"])

    console.print("\n=== OBA Core Analysis Complete (All Phases) ===\n")
>>>>>>> a8a001c (feat: add Phase 2 (Platform Foundation) and Phase 3 (Governance & Accountability Intelligence))


if __name__ == "__main__":
    main()
