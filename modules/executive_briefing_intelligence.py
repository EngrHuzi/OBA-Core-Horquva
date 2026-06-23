import io
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from modules.context_intelligence import run_context_intelligence, ContextIntelligenceResult
from modules.storage_layer import IntelligenceStorage

if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)


@dataclass
class BriefingSection:
    title: str
    content: str
    priority: str
    data_points: list[str]


@dataclass
class ExecutiveBriefing:
    organization: str
    generated_at: str
    executive_summary: str
    sections: list[BriefingSection]
    key_metrics: dict[str, Any]
    top_risks: list[str]
    top_actions: list[str]
    health_trajectory: str


def generate_briefing(context: ContextIntelligenceResult) -> ExecutiveBriefing:
    org = context.organization_context
    sections = []

    risk_assets = [e for e in context.entity_contexts if e.risk_indicators]
    critical_assets = [e for e in context.entity_contexts if e.criticality == "critical"]
    orphaned = [e for e in context.entity_contexts if e.entity_type == "agent" and not e.owner]
    undocumented = [e for e in context.entity_contexts if not e.documented and e.entity_type in ("agent", "workflow")]
    human_spofs = [p for p in context.person_contexts if p.risk_level in ("CRITICAL", "HIGH")]

    sections.append(BriefingSection(
        title="Asset Risk Overview",
        content=f"{len(critical_assets)} critical assets identified. {len(orphaned)} assets fully orphaned with no owner.",
        priority="CRITICAL" if orphaned else "HIGH",
        data_points=[f"{e.entity_name}: {e.criticality}" for e in critical_assets[:5]],
    ))

    sections.append(BriefingSection(
        title="Documentation Gaps",
        content=f"{len(undocumented)} assets lack documentation, creating institutional memory risk.",
        priority="HIGH",
        data_points=[e.entity_name for e in undocumented[:5]],
    ))

    if human_spofs:
        sections.append(BriefingSection(
            title="Human Single Points of Failure",
            content=f"{len(human_spofs)} individuals are critical to operations with insufficient backup.",
            priority="CRITICAL",
            data_points=[f"{p.person_name}: {p.total_responsibilities} responsibilities, {len(p.coverage_gaps)} gaps" for p in human_spofs],
        ))

    gov_governed = [e for e in context.entity_contexts if e.governance_status == "GOVERNED"]
    gov_ungoverned = [e for e in context.entity_contexts if e.governance_status != "GOVERNED" and e.entity_type in ("agent", "workflow", "system")]
    sections.append(BriefingSection(
        title="Governance Coverage",
        content=f"{len(gov_governed)} entities governed. {len(gov_ungoverned)} entities without active governance.",
        priority="WARNING" if gov_ungoverned else "HEALTHY",
        data_points=[f"{e.entity_name}: {e.governance_status}" for e in gov_ungoverned[:3]],
    ))

    actions = []
    if orphaned:
        actions.append(f"URGENT: Assign owners to {', '.join(o.entity_name for o in orphaned[:2])}")
    if human_spofs:
        actions.append(f"HIGH: Redistribute {human_spofs[0].person_name}'s workload ({human_spofs[0].total_responsibilities} responsibilities)")
    if undocumented:
        actions.append(f"MEDIUM: Document {len(undocumented)} undocumented assets")
    if gov_ungoverned:
        actions.append(f"MEDIUM: Establish governance for {len(gov_ungoverned)} ungoverned entities")

    health_parts = org.health_summary.split("—")
    health_num = int(health_parts[0].strip().split("/")[0]) if health_parts else 0

    summary = f"{org.company} has {org.total_entities} entities and {org.total_relationships} relationships. "
    summary += f"Health Score: {org.health_summary}. "
    if orphaned:
        summary += f"{len(orphaned)} orphaned assets require immediate attention. "
    if human_spofs:
        summary += f"{human_spofs[0].person_name} is the highest-risk individual."
    else:
        summary += "No critical human SPOFs identified."

    return ExecutiveBriefing(
        organization=org.company,
        generated_at="2026-06-23",
        executive_summary=summary,
        sections=sections,
        key_metrics={
            "health_score": org.health_summary,
            "total_entities": org.total_entities,
            "total_relationships": org.total_relationships,
            "critical_assets": len(critical_assets),
            "orphaned_assets": len(orphaned),
            "undocumented_assets": len(undocumented),
            "human_spofs": len(human_spofs),
        },
        top_risks=[s.content for s in sections if s.priority in ("CRITICAL", "HIGH")],
        top_actions=actions,
        health_trajectory=f"Current: {health_num}/100. {'Stable' if health_num >= 60 else 'Needs attention'}.",
    )


def run_executive_briefing(data_path: str) -> ExecutiveBriefing:
    with open(data_path) as f:
        data = json.load(f)

    context = run_context_intelligence(data_path)
    briefing = generate_briefing(context)

    storage = IntelligenceStorage()
    storage.save_analysis("executive_briefing", {
        "company": data["company"],
        "health_score": briefing.key_metrics["health_score"],
        "total_entities": briefing.key_metrics["total_entities"],
        "top_actions": briefing.top_actions,
    })

    return briefing


def display_briefing_report(briefing: ExecutiveBriefing):
    console.print(Panel(
        f"[bold cyan]MODULE 23 — EXECUTIVE BRIEFING INTELLIGENCE[/bold cyan]\n[dim]{briefing.organization}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        briefing.executive_summary,
        title="[bold]Executive Summary[/bold]",
        box=box.ROUNDED,
    ))

    console.print(Panel("[bold cyan]KEY METRICS[/bold cyan]", box=box.SIMPLE))

    metric_table = Table(box=box.SIMPLE_HEAVY, show_lines=False)
    metric_table.add_column("Metric", style="white", min_width=24)
    metric_table.add_column("Value", min_width=20)

    for key, value in briefing.key_metrics.items():
        metric_table.add_row(key.replace("_", " ").title(), str(value))

    console.print(metric_table)

    console.print(Panel("[bold cyan]BRIEFING SECTIONS[/bold cyan]", box=box.SIMPLE))

    priority_colors = {"CRITICAL": "bold red", "HIGH": "red", "WARNING": "yellow", "MEDIUM": "blue", "HEALTHY": "green"}

    for section in briefing.sections:
        color = priority_colors.get(section.priority, "white")
        console.print(Panel(
            f"[bold]{section.title}[/bold] [{color}]({section.priority})[/{color}]\n"
            f"{section.content}\n"
            + "\n".join(f"  [dim]-[/dim] {dp}" for dp in section.data_points),
            box=box.ROUNDED,
        ))

    console.print(Panel("[bold cyan]RECOMMENDED ACTIONS[/bold cyan]", box=box.SIMPLE))
    for i, action in enumerate(briefing.top_actions, 1):
        console.print(f"  [bold]{i}.[/bold] {action}")

    console.print(Panel(
        f"[bold]Health Trajectory:[/bold] {briefing.health_trajectory}\n"
        f"[bold]Generated:[/bold] {briefing.generated_at}",
        title="[bold]Briefing Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
    briefing = run_executive_briefing("data/sunrise_care.json")
    display_briefing_report(briefing)
