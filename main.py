import io
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from modules.ownership_intelligence import run_ownership_intelligence, display_ownership_report
from modules.dependency_intelligence import run_dependency_intelligence, display_dependency_report
from modules.risk_intelligence import run_risk_intelligence, display_risk_report
from modules.recommendation_engine import generate_recommendations, display_recommendation_report
from modules.whatif_simulation import run_whatif_simulation, display_whatif_report
from modules.human_agent_map import run_human_agent_map, display_human_agent_map
from modules.ai_tool_intelligence import run_ai_tool_intelligence, display_ai_tool_report
from modules.workflow_intelligence import run_workflow_intelligence, display_workflow_report
from modules.knowledge_risk_intelligence import run_knowledge_risk_intelligence, display_knowledge_risk_report
from modules.organizational_memory_intelligence import run_organizational_memory_intelligence, display_organizational_memory_report
from modules.governance_intelligence import run_governance_intelligence, display_governance_report
from modules.accountability_intelligence import run_accountability_intelligence, display_accountability_report
from modules.ontology_layer import run_ontology_intelligence, display_ontology_report
from modules.relationship_layer import run_relationship_intelligence, display_relationship_report
from modules.context_intelligence import run_context_intelligence, display_context_report
from modules.executive_avatar_intelligence import run_executive_avatar, display_avatar_report
from modules.voice_intelligence import run_voice_intelligence, display_voice_report
from modules.executive_briefing_intelligence import run_executive_briefing, display_briefing_report
from modules.executive_context_intelligence import run_executive_context_intelligence, display_context_intelligence_report
from modules.universal_dependency_graph import run_universal_dependency_graph, display_universal_dep_report
from modules.org_relationship_intelligence import run_org_relationship_intelligence, display_org_relationship_report
from modules.ecosystem_intelligence import run_ecosystem_intelligence, display_ecosystem_report
from modules.hidden_dependency_intelligence import run_hidden_dependency_intelligence, display_hidden_dep_report
from modules.network_intelligence import run_network_intelligence, display_network_report

from modules.platform_orchestrator import get_orchestrator, initialize_platform, ExecutionMode
from modules.knowledge_graph import get_knowledge_graph
from modules.intelligence_exchange import get_protocol
from modules.brain_bridge import run_full_intelligence_pipeline

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)

DATA_PATH = "data/sunrise_care.json"


def display_brain_summary(health_score: int, total_nodes: int, total_edges: int, total_insights: int, total_messages: int):
    console.print(Panel(
        "[bold cyan]ORGANIZATIONAL BRAIN — EXECUTION SUMMARY[/bold cyan]",
        box=box.DOUBLE,
    ))
    
    table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    table.add_column("Metric", style="white", min_width=30)
    table.add_column("Value", style="cyan", min_width=20)
    
    table.add_row("Organizational Health Score", f"{health_score}/100")
    table.add_row("Knowledge Graph Nodes", str(total_nodes))
    table.add_row("Knowledge Graph Edges", str(total_edges))
    table.add_row("Insights Generated", str(total_insights))
    table.add_row("Protocol Messages", str(total_messages))
    table.add_row("Modules Executed", "25")
    table.add_row("Pipeline Status", "[bold green]COMPLETE[/bold green]")
    
    console.print(table)
    console.print()


def run_legacy_mode():
    with open(DATA_PATH) as f:
        data = json.load(f)

    company = data["company"]
    console.print("\n=== OBA CORE — AI WORKFORCE INTELLIGENCE ===\n")

    # Phase 1 — Module 1
    ownership_results = run_ownership_intelligence(DATA_PATH)
    display_ownership_report(ownership_results, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 2
    dependency_results = run_dependency_intelligence(DATA_PATH)
    display_dependency_report(dependency_results, data)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 3
    risk_results, health_score = run_risk_intelligence(DATA_PATH)
    display_risk_report(risk_results, health_score, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 4
    recommendations = generate_recommendations(risk_results, data)
    display_recommendation_report(recommendations, risk_results, health_score, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 5
    scenarios, baseline_health = run_whatif_simulation(DATA_PATH)
    display_whatif_report(scenarios, baseline_health, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 6
    profiles, gaps, results = run_human_agent_map(DATA_PATH)
    display_human_agent_map(profiles, gaps, results, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 7
    tool_risks, dep_maps, dept_tool_map = run_ai_tool_intelligence(DATA_PATH)
    display_ai_tool_report(tool_risks, dep_maps, dept_tool_map, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 8
    wf_risks, node_failures = run_workflow_intelligence(DATA_PATH)
    display_workflow_report(wf_risks, node_failures, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 9
    knowledge_nodes, knowledge_gaps, knowledge_summary = run_knowledge_risk_intelligence(DATA_PATH)
    display_knowledge_risk_report(knowledge_nodes, knowledge_gaps, knowledge_summary, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 1 — Module 10
    memory_nodes, memory_carriers, memory_health = run_organizational_memory_intelligence(DATA_PATH)
    display_organizational_memory_report(memory_nodes, memory_carriers, memory_health, company)
    console.print("\n" + "-" * 60 + "\n")

    console.print("\n" + "=" * 60)
    console.print("[bold cyan]PHASE 2 & 3 — GOVERNANCE & ACCOUNTABILITY PILLAR[/bold cyan]")
    console.print("=" * 60 + "\n")

    # Phase 3 — Module 19: Governance Intelligence
    gov_results, gov_score, gov_risks, dept_heatmap = run_governance_intelligence(DATA_PATH)
    display_governance_report(gov_results, gov_score, gov_risks, dept_heatmap, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 3 — Module 20: Accountability Intelligence
    acc_results, acc_score, chains, person_coverage = run_accountability_intelligence(DATA_PATH)
    display_accountability_report(acc_results, acc_score, chains, person_coverage, company)
    console.print("\n" + "-" * 60 + "\n")

    console.print("\n" + "=" * 60)
    console.print("[bold cyan]ONTOLOGY LAYER — ORGANIZATIONAL BRAIN FOUNDATION[/bold cyan]")
    console.print("=" * 60 + "\n")

    # Ontology Layer
    ontology_result = run_ontology_intelligence(DATA_PATH)
    display_ontology_report(ontology_result, company)
    console.print("\n" + "-" * 60 + "\n")

    # Relationship Layer
    rel_summary, rel_graph = run_relationship_intelligence(DATA_PATH)
    display_relationship_report(rel_summary, company)
    console.print("\n" + "-" * 60 + "\n")

    # Context Intelligence Layer + Voice Agent Context
    context_result = run_context_intelligence(DATA_PATH)
    display_context_report(context_result, company)
    console.print("\n" + "-" * 60 + "\n")

    console.print("\n" + "=" * 60)
    console.print("[bold cyan]PHASE 4 — EXECUTIVE AVATAR & VOICE INTELLIGENCE[/bold cyan]")
    console.print("=" * 60 + "\n")

    # Phase 4 — Module 21: Executive Avatar Intelligence
    avatar_session = run_executive_avatar(DATA_PATH)
    display_avatar_report(avatar_session)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 4 — Module 22: Voice Intelligence Engine
    voice_commands, voice_metrics = run_voice_intelligence(DATA_PATH)
    display_voice_report(voice_commands, voice_metrics, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 4 — Module 23: Executive Briefing Intelligence
    briefing = run_executive_briefing(DATA_PATH)
    display_briefing_report(briefing)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 4 — Module 27: Executive Context Intelligence
    exec_ctx_result = run_executive_context_intelligence(DATA_PATH)
    display_context_intelligence_report(exec_ctx_result, company)
    console.print("\n" + "-" * 60 + "\n")

    console.print("\n" + "=" * 60)
    console.print("[bold cyan]PHASE 5 — ORGANIZATIONAL SCALE INTELLIGENCE[/bold cyan]")
    console.print("=" * 60 + "\n")

    # Phase 5 — Module 28: Universal Dependency Graph
    universal_dep = run_universal_dependency_graph(DATA_PATH)
    display_universal_dep_report(universal_dep, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 5 — Module 29: Organizational Relationship Intelligence
    org_rel = run_org_relationship_intelligence(DATA_PATH)
    display_org_relationship_report(org_rel, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 5 — Module 31: Organizational Ecosystem Intelligence
    ecosystem = run_ecosystem_intelligence(DATA_PATH)
    display_ecosystem_report(ecosystem, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 5 — Module 34: Hidden Dependency Intelligence
    hidden_dep = run_hidden_dependency_intelligence(DATA_PATH)
    display_hidden_dep_report(hidden_dep, company)
    console.print("\n" + "-" * 60 + "\n")

    # Phase 5 — Module 35: Organizational Network Intelligence
    network = run_network_intelligence(DATA_PATH)
    display_network_report(network, company)

    console.print("\n=== OBA Core Analysis Complete (All Phases + Ontology) ===\n")


def main():
    if "--brain" in sys.argv:
        console.print(Panel(
            "[bold cyan]ORGANIZATIONAL BRAIN — UNIFIED INTELLIGENCE ENGINE[/bold cyan]\n"
            "[dim]Module Registry · Capability Registry · Intelligence Exchange · Knowledge Graph[/dim]",
            box=box.DOUBLE,
        ))
        
        result = run_full_intelligence_pipeline(DATA_PATH)
        
        display_brain_summary(
            health_score=result["health_score"],
            total_nodes=result["total_nodes"],
            total_edges=result["total_edges"],
            total_insights=result["total_insights"],
            total_messages=result["total_messages"],
        )
    else:
        run_legacy_mode()


if __name__ == "__main__":
    main()
