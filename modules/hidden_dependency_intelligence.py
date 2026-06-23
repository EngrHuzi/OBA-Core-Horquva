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
class HiddenDependency:
    source_id: str
    source_name: str
    source_type: str
    target_id: str
    target_name: str
    target_type: str
    detection_method: str
    risk_level: str
    description: str


@dataclass
class HiddenDepResult:
    total_hidden: int
    hidden_deps: list[HiddenDependency]
    risk_distribution: dict[str, int]


def run_hidden_dependency_intelligence(data_path: str) -> HiddenDepResult:
    with open(data_path) as f:
        data = json.load(f)

    ontology = build_ontology(data)
    graph = build_relationship_graph(ontology)

    hidden = []

    shared_owners = defaultdict(list)
    for agent in data.get("agents", []):
        if agent.get("owner"):
            shared_owners[agent["owner"]].append(agent)

    for owner, agents in shared_owners.items():
        if len(agents) >= 2:
            for i in range(len(agents)):
                for j in range(i + 1, len(agents)):
                    a1, a2 = agents[i], agents[j]
                    direct_dep = any(
                        (d["from"] == a1["id"] and d["to"] == a2["id"]) or
                        (d["from"] == a2["id"] and d["to"] == a1["id"])
                        for d in data.get("dependencies", [])
                    )
                    if not direct_dep:
                        hidden.append(HiddenDependency(
                            source_id=a1["id"],
                            source_name=a1["name"],
                            source_type="agent",
                            target_id=a2["id"],
                            target_name=a2["name"],
                            target_type="agent",
                            detection_method="shared_owner",
                            risk_level="HIGH",
                            description=f"Both owned by {owner} — removal of owner impacts both",
                        ))

    tool_agents = defaultdict(list)
    for tool in data.get("ai_tools", []):
        for agent_id in tool.get("agents_using", []):
            tool_agents[agent_id].append(tool["name"])

    for agent in data.get("agents", []):
        tools = tool_agents.get(agent["id"], [])
        if len(tools) >= 2:
            for dep in data.get("dependencies", []):
                if dep["from"] == agent["id"]:
                    target = next((a for a in data.get("agents", []) if a["id"] == dep["to"]), None)
                    if target:
                        target_tools = tool_agents.get(target["id"], [])
                        shared = set(tools) & set(target_tools)
                        if shared:
                            hidden.append(HiddenDependency(
                                source_id=agent["id"],
                                source_name=agent["name"],
                                source_type="agent",
                                target_id=target["id"],
                                target_name=target["name"],
                                target_type="agent",
                                detection_method="shared_tool",
                                risk_level="MEDIUM",
                                description=f"Shared tool dependency via: {', '.join(shared)}",
                            ))

    risk_dist = defaultdict(int)
    for h in hidden:
        risk_dist[h.risk_level] += 1

    storage = IntelligenceStorage()
    storage.save_analysis("hidden_dependency", {
        "company": data["company"],
        "total_hidden": len(hidden),
        "risk_distribution": dict(risk_dist),
    })

    return HiddenDepResult(
        total_hidden=len(hidden),
        hidden_deps=hidden,
        risk_distribution=dict(risk_dist),
    )


def display_hidden_dep_report(result: HiddenDepResult, company: str):
    console.print(Panel(
        f"[bold cyan]MODULE 34 — HIDDEN DEPENDENCY INTELLIGENCE[/bold cyan]\n[dim]{company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Hidden Dependencies Found:[/bold] {result.total_hidden}\n"
        + "\n".join(f"[bold]{k}:[/bold] {v}" for k, v in result.risk_distribution.items()),
        title="[bold]Hidden Dependency Summary[/bold]",
        box=box.ROUNDED,
    ))

    if result.hidden_deps:
        table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
        table.add_column("Source", style="white", min_width=24)
        table.add_column("Target", style="white", min_width=24)
        table.add_column("Detection", min_width=16)
        table.add_column("Risk", justify="center", min_width=8)
        table.add_column("Description", min_width=36)

        for h in result.hidden_deps[:15]:
            risk_color = "red" if h.risk_level == "CRITICAL" else "yellow" if h.risk_level == "HIGH" else "blue"
            table.add_row(
                h.source_name,
                h.target_name,
                h.detection_method,
                f"[{risk_color}]{h.risk_level}[/{risk_color}]",
                h.description[:40],
            )
        console.print(table)

    console.print(Panel(
        f"[bold]Hidden dependency intelligence surfaces unseen organizational risks.[/bold]",
        title="[bold]Hidden Dependency Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    result = run_hidden_dependency_intelligence("data/sunrise_care.json")
    display_hidden_dep_report(result, "Sunrise Care")
