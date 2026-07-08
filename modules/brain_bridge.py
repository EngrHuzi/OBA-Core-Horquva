from __future__ import annotations
from typing import Any, Optional
import json

from modules.platform_orchestrator import get_orchestrator, initialize_platform
from modules.module_registry import ModulePhase, get_registry
from modules.capability_registry import CapabilityType, DataType, get_capability_registry
from modules.intelligence_exchange import (
    SignalType,
    MessagePriority,
    get_protocol,
)
from modules.knowledge_graph import (
    GraphNodeType,
    GraphEdgeType,
    InsightSeverity,
    get_knowledge_graph,
    GraphNode,
    GraphEdge,
    GraphInsight,
)

from modules.ownership_intelligence import run_ownership_intelligence
from modules.dependency_intelligence import run_dependency_intelligence
from modules.risk_intelligence import run_risk_intelligence
from modules.recommendation_engine import generate_recommendations
from modules.whatif_simulation import run_whatif_simulation
from modules.human_agent_map import run_human_agent_map
from modules.ai_tool_intelligence import run_ai_tool_intelligence
from modules.workflow_intelligence import run_workflow_intelligence
from modules.knowledge_risk_intelligence import run_knowledge_risk_intelligence
from modules.organizational_memory_intelligence import run_organizational_memory_intelligence
from modules.governance_intelligence import run_governance_intelligence
from modules.accountability_intelligence import run_accountability_intelligence
from modules.ontology_layer import run_ontology_intelligence
from modules.relationship_layer import run_relationship_intelligence
from modules.context_intelligence import run_context_intelligence
from modules.executive_avatar_intelligence import run_executive_avatar
from modules.voice_intelligence import run_voice_intelligence
from modules.executive_briefing_intelligence import run_executive_briefing
from modules.executive_context_intelligence import run_executive_context_intelligence
from modules.universal_dependency_graph import run_universal_dependency_graph
from modules.org_relationship_intelligence import run_org_relationship_intelligence
from modules.ecosystem_intelligence import run_ecosystem_intelligence
from modules.hidden_dependency_intelligence import run_hidden_dependency_intelligence
from modules.network_intelligence import run_network_intelligence


def bridge_ownership_to_graph(results: list, data_path: str):
    graph = get_knowledge_graph()
    protocol = get_protocol()
    
    for result in results:
        node = GraphNode(
            node_id=f"ownership_{result.agent_id}",
            node_type=GraphNodeType.INSIGHT,
            name=f"Ownership Risk: {result.agent_name}",
            properties={
                "agent_id": result.agent_id,
                "agent_name": result.agent_name,
                "owner": result.owner,
                "backup_owner": result.backup_owner,
                "risk_level": result.risk_level,
                "risk_reasons": result.risk_reasons,
            },
            source_module="M01",
        )
        graph.add_node(node)
        
        if result.risk_level in ("CRITICAL", "HIGH"):
            protocol.emit_signal(
                source_module="M01",
                signal_type=SignalType.RISK_DETECTED,
                payload={
                    "agent_id": result.agent_id,
                    "agent_name": result.agent_name,
                    "risk_level": result.risk_level,
                    "risk_type": "ownership",
                },
                priority=MessagePriority.HIGH if result.risk_level == "CRITICAL" else MessagePriority.NORMAL,
            )


def bridge_dependency_to_graph(results: dict, data_path: str):
    graph = get_knowledge_graph()
    protocol = get_protocol()
    
    for dep in results.get("dependencies", []):
        graph.add_edge(GraphEdge(
            edge_id=f"dep_{dep.get('source', '')}_{dep.get('target', '')}",
            source_id=dep.get("source", ""),
            target_id=dep.get("target", ""),
            edge_type=GraphEdgeType.DEPENDS_ON,
            properties=dep,
            source_module="M02",
        ))
    
    for spof in results.get("single_points_of_failure", []):
        protocol.emit_signal(
            source_module="M02",
            signal_type=SignalType.SPOF_DETECTED,
            payload=spof,
            priority=MessagePriority.HIGH,
        )


def bridge_risk_to_graph(results: list, health_score: int, data_path: str):
    graph = get_knowledge_graph()
    protocol = get_protocol()
    
    for result in results:
        node = GraphNode(
            node_id=f"risk_{result.get('agent_id', '')}",
            node_type=GraphNodeType.RISK,
            name=f"Risk Score: {result.get('agent_name', '')}",
            properties=result,
            source_module="M03",
        )
        graph.add_node(node)
    
    protocol.emit_signal(
        source_module="M03",
        signal_type=SignalType.HEALTH_SCORE_CHANGED,
        payload={"health_score": health_score},
    )
    
    if health_score < 60:
        graph.add_insight(GraphInsight(
            insight_id="health_risk",
            title=f"Organizational Health: {health_score}/100",
            description="Health score indicates significant organizational risk",
            severity=InsightSeverity.CRITICAL if health_score < 40 else InsightSeverity.WARNING,
            source_module="M03",
            recommendation="Review and address critical risk factors",
        ))


def bridge_recommendations_to_graph(recommendations: list, data_path: str):
    graph = get_knowledge_graph()
    
    for i, rec in enumerate(recommendations[:10]):
        graph.add_node(GraphNode(
            node_id=f"rec_{i}",
            node_type=GraphNodeType.RECOMMENDATION,
            name=f"Recommendation {i+1}",
            properties=rec if isinstance(rec, dict) else {"text": str(rec)},
            source_module="M04",
        ))


def bridge_governance_to_graph(results: dict, score: int, data_path: str):
    graph = get_knowledge_graph()
    protocol = get_protocol()
    
    for entity_id, entity_data in results.items():
        if isinstance(entity_data, dict):
            graph.add_node(GraphNode(
                node_id=f"governance_{entity_id}",
                node_type=GraphNodeType.GOVERNANCE,
                name=f"Governance: {entity_data.get('name', entity_id)}",
                properties=entity_data,
                source_module="M19",
            ))
    
    protocol.emit_signal(
        source_module="M19",
        signal_type=SignalType.GOVERNANCE_GAP,
        payload={"governance_score": score},
    )


def bridge_universal_dep_to_graph(results: dict, data_path: str):
    graph = get_knowledge_graph()
    
    for node_data in results.get("nodes", []):
        graph.add_node(GraphNode(
            node_id=f"unidep_{node_data.get('id', '')}",
            node_type=GraphNodeType.DEPENDENCY,
            name=f"Dependency: {node_data.get('name', '')}",
            properties=node_data,
            source_module="M28",
        ))
    
    for edge_data in results.get("edges", []):
        graph.add_edge(GraphEdge(
            edge_id=f"unidep_edge_{edge_data.get('source', '')}_{edge_data.get('target', '')}",
            source_id=f"unidep_{edge_data.get('source', '')}",
            target_id=f"unidep_{edge_data.get('target', '')}",
            edge_type=GraphEdgeType.DEPENDS_ON,
            properties=edge_data,
            source_module="M28",
        ))


def bridge_network_to_graph(results: dict, data_path: str):
    graph = get_knowledge_graph()
    
    for node_data in results.get("nodes", []):
        graph.add_node(GraphNode(
            node_id=f"network_{node_data.get('id', '')}",
            node_type=GraphNodeType.ENTITY,
            name=f"Network: {node_data.get('name', '')}",
            properties=node_data,
            source_module="M35",
        ))


def run_full_intelligence_pipeline(data_path: str = "data/sunrise_care.json"):
    orchestrator = get_orchestrator()
    orchestrator.initialize(data_path)
    
    print("\n" + "=" * 70)
    print("ORGANIZATIONAL BRAIN — INTELLIGENCE PIPELINE")
    print("=" * 70 + "\n")
    
    print("[Phase 1] Core Intelligence Modules...")
    
    ownership_results = run_ownership_intelligence(data_path)
    bridge_ownership_to_graph(ownership_results, data_path)
    print(f"  ✓ M01: Ownership Intelligence — {len(ownership_results)} agents analyzed")
    
    dependency_results = run_dependency_intelligence(data_path)
    bridge_dependency_to_graph(dependency_results, data_path)
    print(f"  ✓ M02: Dependency Intelligence — {len(dependency_results.get('dependencies', []))} dependencies mapped")
    
    risk_results, health_score = run_risk_intelligence(data_path)
    bridge_risk_to_graph(risk_results, health_score, data_path)
    print(f"  ✓ M03: Risk Intelligence — Health Score: {health_score}/100")
    
    recommendations = generate_recommendations(risk_results, {"agents": [r.__dict__ if hasattr(r, '__dict__') else r for r in risk_results]})
    bridge_recommendations_to_graph(recommendations, data_path)
    print(f"  ✓ M04: Recommendation Engine — {len(recommendations)} recommendations")
    
    scenarios, baseline_health = run_whatif_simulation(data_path)
    print(f"  ✓ M05: What-If Simulation — {len(scenarios)} scenarios")
    
    profiles, gaps, results = run_human_agent_map(data_path)
    print(f"  ✓ M06: Human-Agent Map — {len(profiles)} profiles, {len(gaps)} gaps")
    
    tool_risks, dep_maps, dept_tool_map = run_ai_tool_intelligence(data_path)
    print(f"  ✓ M07: AI Tool Intelligence — {len(tool_risks)} tools analyzed")
    
    wf_risks, node_failures = run_workflow_intelligence(data_path)
    print(f"  ✓ M08: Workflow Intelligence — {len(wf_risks)} workflows")
    
    knowledge_nodes, knowledge_gaps, knowledge_summary = run_knowledge_risk_intelligence(data_path)
    print(f"  ✓ M09: Knowledge Risk — {len(knowledge_gaps)} gaps identified")
    
    memory_nodes, memory_carriers, memory_health = run_organizational_memory_intelligence(data_path)
    print(f"  ✓ M10: Organizational Memory — Score: {memory_health}")
    
    print("\n[Phase 3] Governance & Accountability...")
    
    gov_results, gov_score, gov_risks, dept_heatmap = run_governance_intelligence(data_path)
    bridge_governance_to_graph(gov_results, gov_score, data_path)
    print(f"  ✓ M19: Governance Intelligence — Score: {gov_score}/100")
    
    acc_results, acc_score, chains, person_coverage = run_accountability_intelligence(data_path)
    print(f"  ✓ M20: Accountability Intelligence — Score: {acc_score}/100")
    
    print("\n[Architecture] Foundation Layers...")
    
    ontology_result = run_ontology_intelligence(data_path)
    print(f"  ✓ Ontology Layer — {ontology_result.get('total_entities', 0)} entities, {ontology_result.get('total_relationships', 0)} relationships")
    
    rel_summary, rel_graph = run_relationship_intelligence(data_path)
    print(f"  ✓ Relationship Layer — Graph analysis complete")
    
    context_result = run_context_intelligence(data_path)
    print(f"  ✓ Context Intelligence — Context packages generated")
    
    print("\n[Phase 4] Executive Avatar & Voice...")
    
    avatar_session = run_executive_avatar(data_path)
    print(f"  ✓ M21: Executive Avatar — Session initialized")
    
    voice_commands, voice_metrics = run_voice_intelligence(data_path)
    print(f"  ✓ M22: Voice Intelligence — {voice_metrics.get('commands_processed', 0)} commands")
    
    briefing = run_executive_briefing(data_path)
    print(f"  ✓ M23: Executive Briefing — Generated")
    
    exec_ctx_result = run_executive_context_intelligence(data_path)
    print(f"  ✓ M27: Executive Context — {exec_ctx_result.get('total_packages', 0)} packages")
    
    print("\n[Phase 5] Organizational Scale...")
    
    universal_dep = run_universal_dependency_graph(data_path)
    bridge_universal_dep_to_graph(universal_dep, data_path)
    print(f"  ✓ M28: Universal Dependency Graph — {universal_dep.get('total_nodes', 0)} nodes, {universal_dep.get('total_edges', 0)} edges")
    
    org_rel = run_org_relationship_intelligence(data_path)
    print(f"  ✓ M29: Org Relationship Intelligence — Complete")
    
    ecosystem = run_ecosystem_intelligence(data_path)
    print(f"  ✓ M31: Ecosystem Intelligence — Complete")
    
    hidden_dep = run_hidden_dependency_intelligence(data_path)
    print(f"  ✓ M34: Hidden Dependency Intelligence — {hidden_dep.get('total_hidden', 0)} hidden deps")
    
    network = run_network_intelligence(data_path)
    bridge_network_to_graph(network, data_path)
    print(f"  ✓ M35: Network Intelligence — Complete")
    
    print("\n" + "=" * 70)
    print("PLATFORM INTEGRATION")
    print("=" * 70 + "\n")
    
    graph = get_knowledge_graph()
    protocol = get_protocol()
    
    graph.add_insight(GraphInsight(
        insight_id="pipeline_complete",
        title="Intelligence Pipeline Complete",
        description="All 25 modules executed successfully. Unified knowledge graph populated.",
        severity=InsightSeverity.INFO,
        source_module="ORCHESTRATOR",
        recommendation="Review knowledge graph for cross-module insights",
    ))
    
    print(f"  Knowledge Graph: {len(graph._nodes)} nodes, {len(graph._edges)} edges")
    print(f"  Insights Generated: {len(graph.get_insights())}")
    print(f"  Protocol Messages: {len(protocol.get_message_log())}")
    
    graph.save("data/knowledge_graph.json")
    print(f"  Knowledge Graph saved to data/knowledge_graph.json")
    
    print("\n" + "=" * 70)
    print("ORGANIZATIONAL BRAIN — PIPELINE COMPLETE")
    print("=" * 70)
    
    return {
        "health_score": health_score,
        "total_nodes": len(graph._nodes),
        "total_edges": len(graph._edges),
        "total_insights": len(graph.get_insights()),
        "total_messages": len(protocol.get_message_log()),
    }
