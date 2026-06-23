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
class EcosystemActor:
    entity_id: str
    entity_name: str
    entity_type: str
    connections: int
    departments: list[str]
    tools_used: list[str]
    agents_owned: list[str]
    risk_score: float


@dataclass
class EcosystemResult:
    total_actors: int
    actors: list[EcosystemActor]
    department_coverage: dict[str, int]
    tool_adoption: dict[str, int]
    ecosystem_health: float


def run_ecosystem_intelligence(data_path: str) -> EcosystemResult:
    with open(data_path) as f:
        data = json.load(f)

    ontology = build_ontology(data)
    graph = build_relationship_graph(ontology)

    actors = []
    dept_coverage = defaultdict(int)
    tool_adoption = defaultdict(int)

    for entity in ontology.entities.values():
        node = graph.nodes.get(entity.entity_id if hasattr(entity, 'entity_id') else entity.id)
        connections = node.total_degree if node else 0

        depts = []
        tools = []
        agents = []

        for rel in ontology.relationships:
            if rel.source_id == (entity.id):
                target = ontology.entities.get(rel.target_id)
                if target:
                    if target.entity_type == "system":
                        tools.append(target.name)
                        tool_adoption[target.name] += 1
                    elif target.entity_type == "agent":
                        agents.append(target.name)
            if rel.target_id == entity.id:
                source = ontology.entities.get(rel.source_id)
                if source and source.entity_type == "system":
                    tools.append(source.name)

        dept = entity.properties.get("department")
        if dept:
            depts.append(dept)
            dept_coverage[dept] += 1

        risk = 0.0
        if connections == 0:
            risk = 0.3
        elif connections >= 8:
            risk = 0.2
        if entity.properties.get("criticality") == "critical":
            risk += 0.2

        actors.append(EcosystemActor(
            entity_id=entity.id,
            entity_name=entity.name,
            entity_type=entity.entity_type,
            connections=connections,
            departments=depts,
            tools_used=list(set(tools)),
            agents_owned=agents,
            risk_score=round(min(1.0, risk), 2),
        ))

    actors.sort(key=lambda a: -a.connections)

    health = 100
    disconnected = sum(1 for a in actors if a.connections == 0)
    health -= disconnected * 5
    health = max(0, health)

    storage = IntelligenceStorage()
    storage.save_analysis("ecosystem", {
        "company": data["company"],
        "total_actors": len(actors),
        "ecosystem_health": health,
    })

    return EcosystemResult(
        total_actors=len(actors),
        actors=actors,
        department_coverage=dict(dept_coverage),
        tool_adoption=dict(tool_adoption),
        ecosystem_health=health,
    )


def display_ecosystem_report(result: EcosystemResult, company: str):
    console.print(Panel(
        f"[bold cyan]MODULE 31 — ORGANIZATIONAL ECOSYSTEM INTELLIGENCE[/bold cyan]\n[dim]{company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Total Actors:[/bold] {result.total_actors}\n"
        f"[bold]Ecosystem Health:[/bold] {result.ecosystem_health}/100",
        title="[bold]Ecosystem Overview[/bold]",
        box=box.ROUNDED,
    ))

    console.print("\n[bold]Department Coverage:[/bold]")
    for dept, count in sorted(result.department_coverage.items(), key=lambda x: -x[1]):
        console.print(f"  [cyan]{dept}[/cyan]: {count} entities")

    console.print("\n[bold]Tool Adoption:[/bold]")
    for tool, count in sorted(result.tool_adoption.items(), key=lambda x: -x[1]):
        console.print(f"  [yellow]{tool}[/yellow]: {count} connections")

    console.print(Panel(
        f"[bold]Ecosystem intelligence maps the complete organizational landscape.[/bold]",
        title="[bold]Ecosystem Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    result = run_ecosystem_intelligence("data/sunrise_care.json")
    display_ecosystem_report(result, "Sunrise Care")
