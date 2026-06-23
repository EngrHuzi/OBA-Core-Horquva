import io
import json
import sys
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box

from modules.ontology_layer import build_ontology
from modules.relationship_layer import build_relationship_graph, RelationshipGraph
from modules.storage_layer import IntelligenceStorage

if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)


@dataclass
class UniversalDepNode:
    entity_id: str
    entity_name: str
    entity_type: str
    upstream_count: int
    downstream_count: int
    cascade_depth: int
    spof_score: float
    is_bottleneck: bool


@dataclass
class UniversalDepResult:
    total_nodes: int
    total_edges: int
    spof_count: int
    bottleneck_count: int
    max_cascade_depth: int
    nodes: list[UniversalDepNode]
    cascade_chains: list[list[str]]
    spof_nodes: list[UniversalDepNode]


def run_universal_dependency_graph(data_path: str) -> UniversalDepResult:
    with open(data_path) as f:
        data = json.load(f)

    ontology = build_ontology(data)
    graph = build_relationship_graph(ontology)

    nodes = []
    for entity_id, entity in ontology.entities.items():
        node = graph.nodes.get(entity_id)
        if not node:
            continue

        upstream = len(graph.reverse_adjacency.get(entity_id, []))
        downstream = len(graph.adjacency.get(entity_id, []))

        cascade_depth = 0
        visited = set()
        queue = [(entity_id, 0)]
        while queue:
            curr, depth = queue.pop(0)
            if curr in visited or depth > 10:
                continue
            visited.add(curr)
            cascade_depth = max(cascade_depth, depth)
            for edge in graph.adjacency.get(curr, []):
                queue.append((edge.target_id, depth + 1))

        spof_score = 0.0
        if downstream >= 3:
            spof_score = min(1.0, downstream / 10.0)
        if upstream == 0 and downstream >= 2:
            spof_score = max(spof_score, 0.7)

        is_bottleneck = spof_score >= 0.5

        nodes.append(UniversalDepNode(
            entity_id=entity_id,
            entity_name=entity.name,
            entity_type=entity.entity_type,
            upstream_count=upstream,
            downstream_count=downstream,
            cascade_depth=cascade_depth,
            spof_score=round(spof_score, 3),
            is_bottleneck=is_bottleneck,
        ))

    nodes.sort(key=lambda n: -n.spof_score)
    spof_nodes = [n for n in nodes if n.spof_score >= 0.5]
    bottleneck_count = len([n for n in nodes if n.is_bottleneck])
    max_depth = max((n.cascade_depth for n in nodes), default=0)

    cascade_chains = []
    for spof in spof_nodes[:3]:
        chain = [spof.entity_name]
        visited = {spof.entity_id}
        queue = [spof.entity_id]
        while queue:
            curr = queue.pop(0)
            for edge in graph.adjacency.get(curr, []):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    target = ontology.entities.get(edge.target_id)
                    if target:
                        chain.append(target.name)
                        queue.append(edge.target_id)
        if len(chain) > 1:
            cascade_chains.append(chain)

    storage = IntelligenceStorage()
    storage.save_analysis("universal_dependency", {
        "company": data["company"],
        "total_nodes": len(nodes),
        "total_edges": len(graph.edges),
        "spof_count": len(spof_nodes),
        "bottleneck_count": bottleneck_count,
        "max_cascade_depth": max_depth,
    })

    return UniversalDepResult(
        total_nodes=len(nodes),
        total_edges=len(graph.edges),
        spof_count=len(spof_nodes),
        bottleneck_count=bottleneck_count,
        max_cascade_depth=max_depth,
        nodes=nodes,
        cascade_chains=cascade_chains,
        spof_nodes=spof_nodes,
    )


def display_universal_dep_report(result: UniversalDepResult, company: str):
    console.print(Panel(
        f"[bold cyan]MODULE 28 — UNIVERSAL DEPENDENCY GRAPH[/bold cyan]\n[dim]{company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Total Nodes:[/bold] {result.total_nodes}\n"
        f"[bold]Total Edges:[/bold] {result.total_edges}\n"
        f"[bold]SPOFs:[/bold] {result.spof_count}\n"
        f"[bold]Bottlenecks:[/bold] {result.bottleneck_count}\n"
        f"[bold]Max Cascade Depth:[/bold] {result.max_cascade_depth}",
        title="[bold]Graph Overview[/bold]",
        box=box.ROUNDED,
    ))

    if result.spof_nodes:
        console.print(Panel("[bold red]SINGLE POINTS OF FAILURE[/bold red]", box=box.SIMPLE))
        table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
        table.add_column("Entity", style="white", min_width=28)
        table.add_column("Type", min_width=10)
        table.add_column("Upstream", justify="center", min_width=10)
        table.add_column("Downstream", justify="center", min_width=12)
        table.add_column("Cascade Depth", justify="center", min_width=14)
        table.add_column("SPOF Score", justify="center", min_width=11)

        for n in result.spof_nodes[:10]:
            score_color = "red" if n.spof_score >= 0.7 else "yellow"
            table.add_row(
                f"[bold]{n.entity_name}[/bold]",
                n.entity_type,
                str(n.upstream_count),
                str(n.downstream_count),
                str(n.cascade_depth),
                f"[{score_color}]{n.spof_score}[/{score_color}]",
            )
        console.print(table)

    if result.cascade_chains:
        console.print("\n[bold]Cascade Chains (Top SPOFs):[/bold]")
        for i, chain in enumerate(result.cascade_chains[:3], 1):
            console.print(f"  [bold]{i}.[/bold] {' -> '.join(chain)}")

    console.print(Panel(
        f"[bold]Universal dependency graph maps ALL organizational dependencies.[/bold]\n"
        f"Identifies SPOFs, bottlenecks, and cascade failure paths.",
        title="[bold]Universal Dependency Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    result = run_universal_dependency_graph("data/sunrise_care.json")
    display_universal_dep_report(result, "Sunrise Care")
