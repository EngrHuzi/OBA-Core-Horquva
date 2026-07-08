import io
import json
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)

DATA_PATH = "data/sunrise_care.json"


def test_module_registry():
    console.print(Panel("[bold cyan]TEST: Module Registry[/bold cyan]", box=box.DOUBLE))
    
    from modules.module_registry import get_registry, ModulePhase
    
    registry = get_registry()
    
    test_modules = [
        ("TEST_01", "Test Module 1", ModulePhase.CORE_INTELLIGENCE, "Test module"),
        ("TEST_02", "Test Module 2", ModulePhase.ARCHITECTURE, "Test architecture module"),
    ]
    
    for module_id, name, phase, desc in test_modules:
        from modules.module_registry import ModuleMetadata
        registry.register(ModuleMetadata(
            module_id=module_id,
            name=name,
            version="1.0.0",
            phase=phase,
            description=desc,
            author="Test",
        ))
    
    summary = registry.get_registry_summary()
    
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Check", style="white")
    table.add_column("Result", style="cyan")
    
    table.add_row("Total Modules Registered", str(summary["total_modules"]))
    table.add_row("Phase Counts", str(summary["phase_counts"]))
    table.add_row("Status Counts", str(summary["status_counts"]))
    table.add_row("Registry JSON Export", "✓" if "modules" in summary else "✗")
    
    console.print(table)
    console.print()
    
    return summary["total_modules"] > 0


def test_capability_registry():
    console.print(Panel("[bold cyan]TEST: Capability Registry[/bold cyan]", box=box.DOUBLE))
    
    from modules.capability_registry import get_capability_registry, CapabilityType, DataType, DataDescriptor
    
    registry = get_capability_registry()
    
    from modules.capability_registry import CapabilityDefinition
    capability = CapabilityDefinition(
        capability_id="test_capability",
        name="Test Capability",
        capability_type=CapabilityType.OUTPUT,
        description="A test capability",
        output_descriptors=[DataDescriptor(data_type=DataType.RISK, format="json")],
    )
    
    registry.register_capability("TEST_01", capability)
    
    summary = registry.get_registry_summary()
    
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Check", style="white")
    table.add_column("Result", style="cyan")
    
    table.add_row("Total Capabilities", str(summary["total_capabilities"]))
    table.add_row("Type Counts", str(summary["type_counts"]))
    table.add_row("Data Type Counts", str(summary["data_type_counts"]))
    table.add_row("Module Coverage", str(summary["module_coverage"]))
    
    console.print(table)
    console.print()
    
    return summary["total_capabilities"] > 0


def test_intelligence_exchange():
    console.print(Panel("[bold cyan]TEST: Intelligence Exchange Protocol[/bold cyan]", box=box.DOUBLE))
    
    from modules.intelligence_exchange import get_protocol, MessageType, SignalType
    
    protocol = get_protocol()
    
    received_messages = []
    
    def test_handler(message):
        received_messages.append(message)
        return {"status": "received"}
    
    protocol.register_handler(
        module_id="TEST_MODULE",
        message_type=MessageType.SIGNAL,
        callback=test_handler,
        filter_signal_type=SignalType.RISK_DETECTED,
    )
    
    message = protocol.emit_signal(
        source_module="TEST_SOURCE",
        signal_type=SignalType.RISK_DETECTED,
        payload={"test": "data"},
    )
    
    summary = protocol.get_exchange_summary()
    
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Check", style="white")
    table.add_column("Result", style="cyan")
    
    table.add_row("Message Emitted", "✓" if message else "✗")
    table.add_row("Handler Registered", "✓" if summary["handler_count"] > 0 else "✗")
    table.add_row("Messages Dispatched", str(summary["total_messages"]))
    table.add_row("Message Type Counts", str(summary["message_type_counts"]))
    table.add_row("Signal Type Counts", str(summary["signal_type_counts"]))
    
    console.print(table)
    console.print()
    
    return summary["total_messages"] > 0


def test_knowledge_graph():
    console.print(Panel("[bold cyan]TEST: Unified Knowledge Graph[/bold cyan]", box=box.DOUBLE))
    
    from modules.knowledge_graph import get_knowledge_graph, GraphNodeType, GraphEdgeType, GraphNode, GraphEdge, InsightSeverity, GraphInsight
    
    graph = get_knowledge_graph()
    
    graph.add_node(GraphNode(
        node_id="test_node_1",
        node_type=GraphNodeType.AGENT,
        name="Test Agent",
        properties={"test": True},
        source_module="TEST",
    ))
    
    graph.add_node(GraphNode(
        node_id="test_node_2",
        node_type=GraphNodeType.PERSON,
        name="Test Person",
        source_module="TEST",
    ))
    
    graph.add_edge(GraphEdge(
        edge_id="test_edge_1",
        source_id="test_node_2",
        target_id="test_node_1",
        edge_type=GraphEdgeType.OWNS,
        source_module="TEST",
    ))
    
    graph.add_insight(GraphInsight(
        insight_id="test_insight",
        title="Test Insight",
        description="A test insight",
        severity=InsightSeverity.INFO,
        source_module="TEST",
    ))
    
    summary = graph.get_graph_summary()
    
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Check", style="white")
    table.add_column("Result", style="cyan")
    
    table.add_row("Total Nodes", str(summary["total_nodes"]))
    table.add_row("Total Edges", str(summary["total_edges"]))
    table.add_row("Node Type Counts", str(summary["node_type_counts"]))
    table.add_row("Edge Type Counts", str(summary["edge_type_counts"]))
    table.add_row("Insights Count", str(summary["insights_count"]))
    table.add_row("Top Central Nodes", str(len(summary["top_central_nodes"])))
    
    console.print(table)
    console.print()
    
    return summary["total_nodes"] > 0


def test_platform_orchestrator():
    console.print(Panel("[bold cyan]TEST: Platform Orchestrator[/bold cyan]", box=box.DOUBLE))
    
    from modules.platform_orchestrator import get_orchestrator
    
    orchestrator = get_orchestrator()
    
    summary = orchestrator.get_orchestration_summary()
    
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Check", style="white")
    table.add_column("Result", style="cyan")
    
    table.add_row("Registry Initialized", "✓" if summary["registry_summary"]["total_modules"] > 0 else "✗")
    table.add_row("Capability Registry", "✓" if summary["capability_summary"]["total_capabilities"] > 0 else "✗")
    table.add_row("Protocol Initialized", "✓" if summary["protocol_summary"]["handler_count"] > 0 else "✗")
    table.add_row("Knowledge Graph", "✓" if summary["graph_summary"]["total_nodes"] > 0 else "✗")
    
    console.print(table)
    console.print()
    
    return summary["registry_summary"]["total_modules"] > 0


def test_full_pipeline():
    console.print(Panel("[bold cyan]TEST: Full Intelligence Pipeline[/bold cyan]", box=box.DOUBLE))
    
    from modules.brain_bridge import run_full_intelligence_pipeline
    
    try:
        result = run_full_intelligence_pipeline(DATA_PATH)
        
        table = Table(box=box.SIMPLE_HEAVY)
        table.add_column("Check", style="white")
        table.add_column("Result", style="cyan")
        
        table.add_row("Health Score", f"{result['health_score']}/100")
        table.add_row("Knowledge Graph Nodes", str(result["total_nodes"]))
        table.add_row("Knowledge Graph Edges", str(result["total_edges"]))
        table.add_row("Insights Generated", str(result["total_insights"]))
        table.add_row("Protocol Messages", str(result["total_messages"]))
        table.add_row("Pipeline Status", "[bold green]SUCCESS[/bold green]")
        
        console.print(table)
        console.print()
        
        return True
    except Exception as e:
        console.print(f"[bold red]Pipeline failed: {e}[/bold red]")
        console.print()
        return False


def main():
    console.print(Panel(
        "[bold cyan]ORGANIZATIONAL BRAIN — COMPONENT TESTS[/bold cyan]\n"
        "[dim]Testing Module Registry, Capability Registry, Intelligence Exchange, Knowledge Graph, Orchestrator[/dim]",
        box=box.DOUBLE,
    ))
    
    results = {}
    
    results["Module Registry"] = test_module_registry()
    results["Capability Registry"] = test_capability_registry()
    results["Intelligence Exchange"] = test_intelligence_exchange()
    results["Knowledge Graph"] = test_knowledge_graph()
    results["Platform Orchestrator"] = test_platform_orchestrator()
    
    console.print(Panel("[bold cyan]TEST: Full Pipeline Integration[/bold cyan]", box=box.DOUBLE))
    results["Full Pipeline"] = test_full_pipeline()
    
    console.print(Panel("[bold cyan]TEST RESULTS SUMMARY[/bold cyan]", box=box.DOUBLE))
    
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Component", style="white")
    table.add_column("Status", style="cyan")
    
    all_passed = True
    for component, passed in results.items():
        status = "[bold green]PASS[/bold green]" if passed else "[bold red]FAIL[/bold red]"
        table.add_row(component, status)
        if not passed:
            all_passed = False
    
    console.print(table)
    console.print()
    
    if all_passed:
        console.print("[bold green]All tests passed! Organizational Brain is operational.[/bold green]")
    else:
        console.print("[bold red]Some tests failed. Check results above.[/bold red]")
    
    console.print()
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
