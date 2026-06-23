import io
import json
import sys
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from modules.ontology_layer import build_ontology
from modules.relationship_layer import build_relationship_graph
from modules.storage_layer import IntelligenceStorage

if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)


@dataclass
class NetworkNode:
    entity_id: str
    entity_name: str
    entity_type: str
    degree_centrality: float
    betweenness_centrality: float
    closeness_centrality: float
    influence_score: float
    role: str


@dataclass
class NetworkCluster:
    cluster_id: int
    members: list[str]
    member_types: list[str]
    internal_edges: int
    cohesion: float


@dataclass
class NetworkResult:
    total_nodes: int
    avg_degree: float
    density: float
    centralization: float
    nodes: list[NetworkNode]
    clusters: list[NetworkCluster]
    influencers: list[NetworkNode]
    isolates: list[str]


def run_network_intelligence(data_path: str) -> NetworkResult:
    with open(data_path) as f:
        data = json.load(f)

    ontology = build_ontology(data)
    graph = build_relationship_graph(ontology)

    n = len(graph.nodes)
    max_edges = n * (n - 1) if n > 1 else 1
    density = len(graph.edges) / max_edges if max_edges > 0 else 0

    max_degree = max((node.total_degree for node in graph.nodes.values()), default=1)
    max_betweenness = 1.0

    betweenness_raw = {}
    for node_id in graph.nodes:
        betweenness_raw[node_id] = 0.0

    for source in graph.nodes:
        for target in graph.nodes:
            if source == target:
                continue
            paths = graph.find_all_paths(source, target, max_depth=5)
            if paths:
                for path in paths:
                    for intermediate in path[1:-1]:
                        betweenness_raw[intermediate] += 1.0 / len(paths)

    max_b = max(betweenness_raw.values()) if betweenness_raw.values() else 1.0
    if max_b > 0:
        for k in betweenness_raw:
            betweenness_raw[k] /= max_b

    network_nodes = []
    for entity_id, node in graph.nodes.items():
        dc = node.total_degree / max_degree if max_degree > 0 else 0
        bc = betweenness_raw.get(entity_id, 0)

        far_count = 0
        reachable = 0
        for other_id in graph.nodes:
            if other_id != entity_id:
                path = graph.bfs(entity_id, other_id)
                if path:
                    reachable += 1
                    far_count += len(path) - 1
                else:
                    far_count += n

        cc = reachable / far_count if far_count > 0 else 0

        influence = (dc * 0.4 + bc * 0.4 + cc * 0.2)

        if bc >= 0.3:
            role = "bridge"
        elif dc >= 0.5:
            role = "hub"
        elif dc <= 0.1:
            role = "peripheral"
        else:
            role = "connector"

        network_nodes.append(NetworkNode(
            entity_id=entity_id,
            entity_name=node.name,
            entity_type=node.entity_type,
            degree_centrality=round(dc, 4),
            betweenness_centrality=round(bc, 4),
            closeness_centrality=round(cc, 4),
            influence_score=round(influence, 4),
            role=role,
        ))

    network_nodes.sort(key=lambda n: -n.influence_score)

    influencers = [n for n in network_nodes if n.influence_score >= 0.3][:5]
    isolates = [n.entity_name for n in network_nodes if n.degree_centrality == 0]

    clusters = []
    visited = set()
    cluster_id = 0
    for node_id in graph.nodes:
        if node_id in visited:
            continue
        cluster_members = []
        queue = [node_id]
        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            cluster_members.append(curr)
            for edge in graph.adjacency.get(curr, []):
                if edge.target_id not in visited:
                    queue.append(edge.target_id)
            for edge in graph.reverse_adjacency.get(curr, []):
                if edge.source_id not in visited:
                    queue.append(edge.source_id)

        if len(cluster_members) > 1:
            internal = 0
            for m1 in cluster_members:
                for m2 in cluster_members:
                    if m1 != m2:
                        for edge in graph.adjacency.get(m1, []):
                            if edge.target_id == m2:
                                internal += 1

            possible = len(cluster_members) * (len(cluster_members) - 1)
            cohesion = internal / possible if possible > 0 else 0

            clusters.append(NetworkCluster(
                cluster_id=cluster_id,
                members=[graph.nodes[m].name for m in cluster_members if m in graph.nodes],
                member_types=[graph.nodes[m].entity_type for m in cluster_members if m in graph.nodes],
                internal_edges=internal,
                cohesion=round(cohesion, 3),
            ))
            cluster_id += 1

    avg_degree = sum(node.total_degree for node in graph.nodes.values()) / n if n > 0 else 0
    centralization = max((node.total_degree for node in graph.nodes.values()), default=0) / (n - 1) if n > 1 else 0

    storage = IntelligenceStorage()
    storage.save_analysis("network", {
        "company": data["company"],
        "total_nodes": n,
        "avg_degree": round(avg_degree, 2),
        "density": round(density, 4),
        "clusters": len(clusters),
        "isolates": len(isolates),
    })

    return NetworkResult(
        total_nodes=n,
        avg_degree=round(avg_degree, 2),
        density=round(density, 4),
        centralization=round(centralization, 4),
        nodes=network_nodes,
        clusters=clusters,
        influencers=influencers,
        isolates=isolates,
    )


def display_network_report(result: NetworkResult, company: str):
    console.print(Panel(
        f"[bold cyan]MODULE 35 — ORGANIZATIONAL NETWORK INTELLIGENCE[/bold cyan]\n[dim]{company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Total Nodes:[/bold] {result.total_nodes}\n"
        f"[bold]Avg Degree:[/bold] {result.avg_degree}\n"
        f"[bold]Density:[/bold] {result.density}\n"
        f"[bold]Centralization:[/bold] {result.centralization}\n"
        f"[bold]Clusters:[/bold] {len(result.clusters)}\n"
        f"[bold]Isolates:[/bold] {len(result.isolates)}",
        title="[bold]Network Overview[/bold]",
        box=box.ROUNDED,
    ))

    if result.influencers:
        console.print(Panel("[bold cyan]TOP INFLUENCERS[/bold cyan]", box=box.SIMPLE))
        table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
        table.add_column("Entity", style="white", min_width=24)
        table.add_column("Type", min_width=10)
        table.add_column("Role", min_width=12)
        table.add_column("Degree Cent.", justify="center", min_width=12)
        table.add_column("Between Cent.", justify="center", min_width=13)
        table.add_column("Influence", justify="center", min_width=10)

        for n in result.influencers:
            table.add_row(
                f"[bold]{n.entity_name}[/bold]",
                n.entity_type,
                n.role,
                f"{n.degree_centrality:.3f}",
                f"{n.betweenness_centrality:.3f}",
                f"{n.influence_score:.3f}",
            )
        console.print(table)

    if result.clusters:
        console.print("\n[bold]Network Clusters:[/bold]")
        for c in result.clusters[:5]:
            types = set(c.member_types)
            console.print(f"  Cluster {c.cluster_id}: {len(c.members)} members ({', '.join(types)}) — cohesion {c.cohesion}")

    if result.isolates:
        console.print(f"\n[bold]Isolated Nodes:[/bold] {', '.join(result.isolates)}")

    console.print(Panel(
        f"[bold]Network intelligence understands how influence, information, and decisions travel.[/bold]",
        title="[bold]Network Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    result = run_network_intelligence("data/sunrise_care.json")
    display_network_report(result, "Sunrise Care")
