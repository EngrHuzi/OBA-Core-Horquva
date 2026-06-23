import io
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box

from modules.ontology_layer import build_ontology, OntologyRegistry, OntologyEntity, OntologyRelationship
from modules.storage_layer import IntelligenceStorage

if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)


@dataclass
class GraphNode:
    id: str
    name: str
    entity_type: str
    in_degree: int = 0
    out_degree: int = 0
    total_degree: int = 0
    neighbors_in: list[str] = field(default_factory=list)
    neighbors_out: list[str] = field(default_factory=list)


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relationship_type: str
    weight: float = 1.0


@dataclass
class PathResult:
    source: str
    target: str
    path: list[str]
    path_names: list[str]
    length: int
    relationship_chain: list[str]


@dataclass
class ConnectivityResult:
    total_nodes: int
    total_edges: int
    connected_components: int
    isolated_nodes: list[str]
    strongest_node: str
    strongest_node_degree: int
    weakest_node: str
    weakest_node_degree: int
    avg_degree: float
    density: float


@dataclass
class CycleResult:
    has_cycles: bool
    cycles: list[list[str]]
    cycle_count: int


@dataclass
class BottleneckResult:
    entity_id: str
    entity_name: str
    entity_type: str
    betweenness_score: float
    paths_through: int
    total_paths: int


@dataclass
class RelationshipSummary:
    connectivity: ConnectivityResult
    cycles: CycleResult
    bottlenecks: list[BottleneckResult]
    top_nodes_by_degree: list[GraphNode]
    top_nodes_by_in_degree: list[GraphNode]
    top_nodes_by_out_degree: list[GraphNode]
    cross_type_edges: int
    intra_type_edges: int
    strongest_connections: list[dict]


class RelationshipGraph:
    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self.adjacency: dict[str, list[GraphEdge]] = defaultdict(list)
        self.reverse_adjacency: dict[str, list[GraphEdge]] = defaultdict(list)

    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)
        self.adjacency[edge.source_id].append(edge)
        self.reverse_adjacency[edge.target_id].append(edge)

        if edge.source_id in self.nodes:
            self.nodes[edge.source_id].out_degree += 1
            self.nodes[edge.source_id].total_degree += 1
            self.nodes[edge.source_id].neighbors_out.append(edge.target_id)

        if edge.target_id in self.nodes:
            self.nodes[edge.target_id].in_degree += 1
            self.nodes[edge.target_id].total_degree += 1
            self.nodes[edge.target_id].neighbors_in.append(edge.source_id)

    def bfs(self, start: str, end: str) -> list[str] | None:
        if start not in self.nodes or end not in self.nodes:
            return None

        visited = {start}
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path

            for edge in self.adjacency.get(current, []):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    queue.append((edge.target_id, path + [edge.target_id]))

        return None

    def find_all_paths(self, start: str, end: str, max_depth: int = 10) -> list[list[str]]:
        if start not in self.nodes or end not in self.nodes:
            return []

        all_paths = []
        self._dfs_paths(start, end, set(), [start], all_paths, max_depth)
        return all_paths

    def _dfs_paths(self, current: str, end: str, visited: set, path: list, all_paths: list, max_depth: int):
        if len(path) > max_depth:
            return

        if current == end and len(path) > 1:
            all_paths.append(list(path))
            return

        for edge in self.adjacency.get(current, []):
            if edge.target_id not in visited:
                visited.add(edge.target_id)
                path.append(edge.target_id)
                self._dfs_paths(edge.target_id, end, visited, path, all_paths, max_depth)
                path.pop()
                visited.discard(edge.target_id)

    def get_neighbors(self, node_id: str, direction: str = "both") -> list[str]:
        neighbors = set()
        if direction in ("out", "both"):
            for edge in self.adjacency.get(node_id, []):
                neighbors.add(edge.target_id)
        if direction in ("in", "both"):
            for edge in self.reverse_adjacency.get(node_id, []):
                neighbors.add(edge.source_id)
        return sorted(neighbors)

    def detect_cycles(self) -> list[list[str]]:
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for edge in self.adjacency.get(node, []):
                if edge.target_id not in visited:
                    dfs(edge.target_id, path)
                elif edge.target_id in rec_stack:
                    cycle_start = path.index(edge.target_id)
                    cycle = path[cycle_start:] + [edge.target_id]
                    cycles.append(cycle)

            path.pop()
            rec_stack.discard(node)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])

        return cycles

    def find_isolated_nodes(self) -> list[str]:
        return [
            node_id for node_id, node in self.nodes.items()
            if node.total_degree == 0
        ]

    def calculate_betweenness(self) -> dict[str, float]:
        betweenness = {node_id: 0.0 for node_id in self.nodes}
        node_list = list(self.nodes.keys())

        for source in node_list:
            for target in node_list:
                if source == target:
                    continue

                paths = self.find_all_paths(source, target, max_depth=6)
                if not paths:
                    continue

                for path in paths:
                    for intermediate in path[1:-1]:
                        betweenness[intermediate] += 1.0 / len(paths)

        max_val = max(betweenness.values()) if betweenness.values() else 1.0
        if max_val > 0:
            for node_id in betweenness:
                betweenness[node_id] /= max_val

        return betweenness

    def get_strongest_connections(self, top_n: int = 10) -> list[dict]:
        connections = []
        for edge in self.edges:
            source = self.nodes.get(edge.source_id)
            target = self.nodes.get(edge.target_id)
            if source and target:
                shared_neighbors = len(set(self.get_neighbors(edge.source_id)) & set(self.get_neighbors(edge.target_id)))
                strength = 1.0 + shared_neighbors * 0.5
                connections.append({
                    "source": source.name,
                    "source_id": edge.source_id,
                    "target": target.name,
                    "target_id": edge.target_id,
                    "relationship": edge.relationship_type,
                    "strength": strength,
                })

        connections.sort(key=lambda x: -x["strength"])
        return connections[:top_n]


def build_relationship_graph(registry: OntologyRegistry) -> RelationshipGraph:
    graph = RelationshipGraph()

    for entity in registry.entities.values():
        graph.add_node(GraphNode(
            id=entity.id,
            name=entity.name,
            entity_type=entity.entity_type,
        ))

    for rel in registry.relationships:
        graph.add_edge(GraphEdge(
            source_id=rel.source_id,
            target_id=rel.target_id,
            relationship_type=rel.relationship_type,
        ))

    return graph


def analyze_connectivity(graph: RelationshipGraph) -> ConnectivityResult:
    visited = set()

    def bfs_component(start: str) -> set:
        component = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node in component:
                continue
            component.add(node)
            for edge in graph.adjacency.get(node, []):
                if edge.target_id not in component:
                    queue.append(edge.target_id)
            for edge in graph.reverse_adjacency.get(node, []):
                if edge.source_id not in component:
                    queue.append(edge.source_id)
        return component

    components = 0
    for node_id in graph.nodes:
        if node_id not in visited:
            component = bfs_component(node_id)
            visited.update(component)
            components += 1

    isolated = graph.find_isolated_nodes()
    degrees = [node.total_degree for node in graph.nodes.values()]
    avg_degree = sum(degrees) / len(degrees) if degrees else 0

    strongest = max(graph.nodes.values(), key=lambda n: n.total_degree) if graph.nodes else None
    weakest_candidates = [n for n in graph.nodes.values() if n.total_degree > 0]
    weakest = min(weakest_candidates, key=lambda n: n.total_degree) if weakest_candidates else None

    n = len(graph.nodes)
    max_edges = n * (n - 1) if n > 1 else 1
    density = len(graph.edges) / max_edges if max_edges > 0 else 0

    return ConnectivityResult(
        total_nodes=len(graph.nodes),
        total_edges=len(graph.edges),
        connected_components=components,
        isolated_nodes=isolated,
        strongest_node=strongest.name if strongest else "N/A",
        strongest_node_degree=strongest.total_degree if strongest else 0,
        weakest_node=weakest.name if weakest else "N/A",
        weakest_node_degree=weakest.total_degree if weakest else 0,
        avg_degree=round(avg_degree, 2),
        density=round(density, 4),
    )


def find_bottlenecks(graph: RelationshipGraph, betweenness: dict[str, float], top_n: int = 5) -> list[BottleneckResult]:
    scored = []
    total_paths = 0
    for source in graph.nodes:
        for target in graph.nodes:
            if source != target:
                paths = graph.find_all_paths(source, target, max_depth=6)
                total_paths += len(paths)

    for node_id, score in betweenness.items():
        if score > 0:
            node = graph.nodes[node_id]
            paths_through = int(score * total_paths) if total_paths > 0 else 0
            scored.append(BottleneckResult(
                entity_id=node_id,
                entity_name=node.name,
                entity_type=node.entity_type,
                betweenness_score=round(score, 4),
                paths_through=paths_through,
                total_paths=total_paths,
            ))

    scored.sort(key=lambda b: -b.betweenness_score)
    return scored[:top_n]


def run_relationship_intelligence(data_path: str) -> tuple[RelationshipSummary, RelationshipGraph]:
    with open(data_path) as f:
        data = json.load(f)

    ontology = build_ontology(data)
    graph = build_relationship_graph(ontology)
    connectivity = analyze_connectivity(graph)
    cycles = graph.detect_cycles()
    betweenness = graph.calculate_betweenness()
    bottlenecks = find_bottlenecks(graph, betweenness)

    top_degree = sorted(graph.nodes.values(), key=lambda n: -n.total_degree)[:5]
    top_in = sorted(graph.nodes.values(), key=lambda n: -n.in_degree)[:5]
    top_out = sorted(graph.nodes.values(), key=lambda n: -n.out_degree)[:5]

    cross_type = 0
    intra_type = 0
    for edge in graph.edges:
        source = graph.nodes.get(edge.source_id)
        target = graph.nodes.get(edge.target_id)
        if source and target:
            if source.entity_type == target.entity_type:
                intra_type += 1
            else:
                cross_type += 1

    strongest = graph.get_strongest_connections(10)

    summary = RelationshipSummary(
        connectivity=connectivity,
        cycles=CycleResult(
            has_cycles=len(cycles) > 0,
            cycles=cycles,
            cycle_count=len(cycles),
        ),
        bottlenecks=bottlenecks,
        top_nodes_by_degree=top_degree,
        top_nodes_by_in_degree=top_in,
        top_nodes_by_out_degree=top_out,
        cross_type_edges=cross_type,
        intra_type_edges=intra_type,
        strongest_connections=strongest,
    )

    storage = IntelligenceStorage()
    storage.save_analysis("relationship", {
        "company": data["company"],
        "total_nodes": connectivity.total_nodes,
        "total_edges": connectivity.total_edges,
        "connected_components": connectivity.connected_components,
        "isolated_nodes": connectivity.isolated_nodes,
        "has_cycles": len(cycles) > 0,
        "cycle_count": len(cycles),
        "bottlenecks": [
            {"entity": b.entity_name, "score": b.betweenness_score}
            for b in bottlenecks
        ],
        "cross_type_edges": cross_type,
        "intra_type_edges": intra_type,
    })

    return summary, graph


def display_relationship_report(summary: RelationshipSummary, company: str):
    console.print(Panel(
        f"[bold cyan]RELATIONSHIP LAYER — ENTITY CONNECTION GRAPH[/bold cyan]\n[dim]Company: {company}[/dim]",
        box=box.DOUBLE,
    ))

    conn = summary.connectivity
    console.print(Panel(
        f"[bold]Total Nodes:[/bold] {conn.total_nodes}\n"
        f"[bold]Total Edges:[/bold] {conn.total_edges}\n"
        f"[bold]Connected Components:[/bold] {conn.connected_components}\n"
        f"[bold]Isolated Nodes:[/bold] {len(conn.isolated_nodes)}\n"
        f"[bold]Avg Degree:[/bold] {conn.avg_degree}\n"
        f"[bold]Graph Density:[/bold] {conn.density}\n"
        f"[bold]Cross-Type Edges:[/bold] {summary.cross_type_edges}\n"
        f"[bold]Intra-Type Edges:[/bold] {summary.intra_type_edges}",
        title="[bold]Graph Connectivity[/bold]",
        box=box.ROUNDED,
    ))

    console.print(Panel("[bold cyan]NODE CENTRALITY — TOP NODES BY DEGREE[/bold cyan]", box=box.SIMPLE))

    table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    table.add_column("Entity", style="white", min_width=28)
    table.add_column("Type", min_width=10)
    table.add_column("In-Degree", justify="center", min_width=10)
    table.add_column("Out-Degree", justify="center", min_width=11)
    table.add_column("Total", justify="center", min_width=7)

    for node in summary.top_nodes_by_degree:
        table.add_row(
            f"[bold]{node.name}[/bold]",
            node.entity_type,
            str(node.in_degree),
            str(node.out_degree),
            str(node.total_degree),
        )

    console.print(table)

    if summary.top_nodes_by_in_degree:
        console.print("\n[bold]Most Depended-On (In-Degree):[/bold]")
        for node in summary.top_nodes_by_in_degree[:3]:
            if node.in_degree > 0:
                console.print(f"  [cyan]{node.name}[/cyan] ({node.entity_type}) — {node.in_degree} incoming relationships")

    if summary.top_nodes_by_out_degree:
        console.print("\n[bold]Most Connected (Out-Degree):[/bold]")
        for node in summary.top_nodes_by_out_degree[:3]:
            if node.out_degree > 0:
                console.print(f"  [yellow]{node.name}[/yellow] ({node.entity_type}) — {node.out_degree} outgoing relationships")

    if summary.bottlenecks:
        console.print(Panel("[bold red]BOTTLENECK ANALYSIS — HIGHEST BETWEENNESS CENTRALITY[/bold red]", box=box.SIMPLE))

        bottleneck_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
        bottleneck_table.add_column("Entity", style="white", min_width=28)
        bottleneck_table.add_column("Type", min_width=10)
        bottleneck_table.add_column("Betweenness", justify="center", min_width=12)
        bottleneck_table.add_column("Paths Through", justify="center", min_width=14)

        for b in summary.bottlenecks:
            bottleneck_table.add_row(
                f"[bold red]{b.entity_name}[/bold red]",
                b.entity_type,
                f"{b.betweenness_score:.4f}",
                f"{b.paths_through}/{b.total_paths}",
            )

        console.print(bottleneck_table)

    cycle_color = "red" if summary.cycles.has_cycles else "green"
    cycle_label = "YES" if summary.cycles.has_cycles else "NO"
    console.print(Panel(
        f"[bold]Cycles Detected:[/bold] [{cycle_color}]{cycle_label}[/{cycle_color}] ({summary.cycles.cycle_count} cycles)\n"
        f"[bold]Isolated Nodes:[/bold] {', '.join(summary.connectivity.isolated_nodes) if summary.connectivity.isolated_nodes else 'None'}\n"
        f"[bold]Strongest Node:[/bold] {summary.connectivity.strongest_node} (degree {summary.connectivity.strongest_node_degree})",
        title="[bold]Graph Health[/bold]",
        box=box.ROUNDED,
    ))

    if summary.strongest_connections:
        console.print(Panel("[bold cyan]STRONGEST CONNECTIONS[/bold cyan]", box=box.SIMPLE))

        conn_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
        conn_table.add_column("Source", style="white", min_width=28)
        conn_table.add_column("Relationship", min_width=16)
        conn_table.add_column("Target", style="white", min_width=28)
        conn_table.add_column("Strength", justify="center", min_width=10)

        for c in summary.strongest_connections:
            conn_table.add_row(
                c["source"],
                c["relationship"],
                c["target"],
                f"{c['strength']:.1f}",
            )

        console.print(conn_table)

    console.print(Panel(
        f"[bold]Graph Summary:[/bold] {conn.total_nodes} nodes, {conn.total_edges} edges, "
        f"{conn.connected_components} components, density {conn.density}\n"
        f"[bold]Cross-type connections:[/bold] {summary.cross_type_edges} | "
        f"[bold]Intra-type connections:[/bold] {summary.intra_type_edges}\n"
        f"[bold]Bottlenecks:[/bold] {len(summary.bottlenecks)} | "
        f"[bold]Cycles:[/bold] {summary.cycles.cycle_count} | "
        f"[bold]Isolated:[/bold] {len(summary.connectivity.isolated_nodes)}",
        title="[bold]Relationship Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
    summary, graph = run_relationship_intelligence("data/sunrise_care.json")
    display_relationship_report(summary, data["company"])
