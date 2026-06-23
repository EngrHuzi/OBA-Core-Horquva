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
class RelationshipHealth:
    relationship_type: str
    total_count: int
    healthy_count: int
    risk_count: int
    health_score: float


@dataclass
class OrgRelationshipResult:
    total_relationships: int
    relationship_types: int
    health_scores: list[RelationshipHealth]
    overall_health: float
    weak_connections: list[dict]
    strong_connections: list[dict]


def run_org_relationship_intelligence(data_path: str) -> OrgRelationshipResult:
    with open(data_path) as f:
        data = json.load(f)

    ontology = build_ontology(data)
    graph = build_relationship_graph(ontology)

    type_groups = defaultdict(list)
    for rel in ontology.relationships:
        type_groups[rel.relationship_type].append(rel)

    health_scores = []
    for rtype, rels in type_groups.items():
        healthy = 0
        risk = 0
        for rel in rels:
            source = ontology.entities.get(rel.source_id)
            target = ontology.entities.get(rel.target_id)
            if source and target:
                if source.entity_type == "human" and target.entity_type == "agent":
                    if target.properties.get("backup_owner"):
                        healthy += 1
                    else:
                        risk += 1
                else:
                    healthy += 1
            else:
                risk += 1

        total = len(rels)
        score = (healthy / total * 100) if total > 0 else 100
        health_scores.append(RelationshipHealth(
            relationship_type=rtype,
            total_count=total,
            healthy_count=healthy,
            risk_count=risk,
            health_score=round(score, 1),
        ))

    overall = sum(h.health_score for h in health_scores) / len(health_scores) if health_scores else 100

    weak = []
    strong = []
    for entity_id, node in graph.nodes.items():
        if node.total_degree <= 1 and node.total_degree > 0:
            weak.append({"name": node.name, "type": node.entity_type, "degree": node.total_degree})
        elif node.total_degree >= 7:
            strong.append({"name": node.name, "type": node.entity_type, "degree": node.total_degree})

    storage = IntelligenceStorage()
    storage.save_analysis("org_relationship", {
        "company": data["company"],
        "total_relationships": len(ontology.relationships),
        "overall_health": round(overall, 1),
    })

    return OrgRelationshipResult(
        total_relationships=len(ontology.relationships),
        relationship_types=len(type_groups),
        health_scores=sorted(health_scores, key=lambda h: h.health_score),
        overall_health=round(overall, 1),
        weak_connections=weak,
        strong_connections=sorted(strong, key=lambda s: -s["degree"]),
    )


def display_org_relationship_report(result: OrgRelationshipResult, company: str):
    console.print(Panel(
        f"[bold cyan]MODULE 29 — ORGANIZATIONAL RELATIONSHIP INTELLIGENCE[/bold cyan]\n[dim]{company}[/dim]",
        box=box.DOUBLE,
    ))

    health_color = "green" if result.overall_health >= 80 else "yellow" if result.overall_health >= 60 else "red"
    console.print(Panel(
        f"[bold]Total Relationships:[/bold] {result.total_relationships}\n"
        f"[bold]Relationship Types:[/bold] {result.relationship_types}\n"
        f"[bold]Overall Health:[/bold] [{health_color}]{result.overall_health}%[/{health_color}]",
        title="[bold]Relationship Health[/bold]",
        box=box.ROUNDED,
    ))

    table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    table.add_column("Relationship Type", style="white", min_width=22)
    table.add_column("Total", justify="center", min_width=8)
    table.add_column("Healthy", justify="center", min_width=9)
    table.add_column("At Risk", justify="center", min_width=8)
    table.add_column("Health", justify="center", min_width=8)

    for h in result.health_scores:
        h_color = "green" if h.health_score >= 80 else "yellow" if h.health_score >= 60 else "red"
        table.add_row(
            h.relationship_type,
            str(h.total_count),
            str(h.healthy_count),
            str(h.risk_count),
            f"[{h_color}]{h.health_score}%[/{h_color}]",
        )
    console.print(table)

    if result.strong_connections:
        console.print("\n[bold]Strongest Connections (degree >= 7):[/bold]")
        for s in result.strong_connections[:5]:
            console.print(f"  [bold]{s['name']}[/bold] ({s['type']}) — degree {s['degree']}")

    console.print(Panel(
        f"[bold]Relationship intelligence understands the nature and health of every connection.[/bold]",
        title="[bold]Org Relationship Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    result = run_org_relationship_intelligence("data/sunrise_care.json")
    display_org_relationship_report(result, "Sunrise Care")
