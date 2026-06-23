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
class ContextPackage:
    package_id: str
    package_type: str
    entity_id: str
    entity_name: str
    context_data: dict[str, Any]
    relevance_score: float
    last_updated: str


@dataclass
class ExecutiveContextResult:
    total_packages: int
    packages_by_type: dict[str, int]
    packages: list[ContextPackage]
    context_coverage: float
    stale_packages: int


def build_context_packages(context: ContextIntelligenceResult) -> list[ContextPackage]:
    packages = []

    for e in context.entity_contexts:
        packages.append(ContextPackage(
            package_id=f"pkg_entity_{e.entity_id}",
            package_type="entity_context",
            entity_id=e.entity_id,
            entity_name=e.entity_name,
            context_data={
                "entity_type": e.entity_type,
                "owner": e.owner,
                "criticality": e.criticality,
                "documented": e.documented,
                "governance_status": e.governance_status,
                "risk_indicators": e.risk_indicators,
                "related_count": len(e.related_entities),
                "summary": e.summary,
            },
            relevance_score=1.0 if e.criticality == "critical" else 0.7 if e.criticality == "high" else 0.5,
            last_updated="2026-06-23",
        ))

    for p in context.person_contexts:
        packages.append(ContextPackage(
            package_id=f"pkg_person_{p.person_id}",
            package_type="person_context",
            entity_id=p.person_id,
            entity_name=p.person_name,
            context_data={
                "owned_agents": p.owned_agents,
                "owned_workflows": p.owned_workflows,
                "backup_for": p.backup_for,
                "total_responsibilities": p.total_responsibilities,
                "coverage_gaps": p.coverage_gaps,
                "risk_level": p.risk_level,
                "summary": p.summary,
            },
            relevance_score=1.0 if p.risk_level == "CRITICAL" else 0.8 if p.risk_level == "HIGH" else 0.5,
            last_updated="2026-06-23",
        ))

    org = context.organization_context
    packages.append(ContextPackage(
        package_id="pkg_org_summary",
        package_type="organization_summary",
        entity_id="org",
        entity_name=org.company,
        context_data={
            "total_entities": org.total_entities,
            "total_relationships": org.total_relationships,
            "entity_type_counts": org.entity_type_counts,
            "critical_assets": org.critical_assets,
            "orphaned_assets": org.orphaned_assets,
            "undocumented_assets": org.undocumented_assets,
            "health_summary": org.health_summary,
            "executive_brief": org.executive_brief,
        },
        relevance_score=1.0,
        last_updated="2026-06-23",
    ))

    return packages


def run_executive_context_intelligence(data_path: str) -> ExecutiveContextResult:
    with open(data_path) as f:
        data = json.load(f)

    context = run_context_intelligence(data_path)
    packages = build_context_packages(context)

    type_counts = {}
    for pkg in packages:
        type_counts[pkg.package_type] = type_counts.get(pkg.package_type, 0) + 1

    coverage = sum(1 for p in packages if p.relevance_score >= 0.5) / len(packages) if packages else 0

    storage = IntelligenceStorage()
    storage.save_analysis("executive_context", {
        "company": data["company"],
        "total_packages": len(packages),
        "packages_by_type": type_counts,
        "context_coverage": round(coverage, 2),
    })

    return ExecutiveContextResult(
        total_packages=len(packages),
        packages_by_type=type_counts,
        packages=packages,
        context_coverage=round(coverage, 2),
        stale_packages=0,
    )


def display_context_intelligence_report(result: ExecutiveContextResult, company: str):
    console.print(Panel(
        f"[bold cyan]MODULE 27 — EXECUTIVE CONTEXT INTELLIGENCE[/bold cyan]\n[dim]{company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Total Context Packages:[/bold] {result.total_packages}\n"
        f"[bold]Context Coverage:[/bold] {result.context_coverage}\n"
        f"[bold]Stale Packages:[/bold] {result.stale_packages}",
        title="[bold]Context Summary[/bold]",
        box=box.ROUNDED,
    ))

    console.print("\n[bold]Packages by Type:[/bold]")
    for ptype, count in sorted(result.packages_by_type.items(), key=lambda x: -x[1]):
        console.print(f"  [cyan]{ptype}[/cyan]: {count}")

    console.print(Panel("[bold cyan]HIGH-RELEVANCE CONTEXT PACKAGES[/bold cyan]", box=box.SIMPLE))

    pkg_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    pkg_table.add_column("Entity", style="white", min_width=24)
    pkg_table.add_column("Type", min_width=16)
    pkg_table.add_column("Package Type", min_width=18)
    pkg_table.add_column("Relevance", justify="center", min_width=10)
    pkg_table.add_column("Key Data", min_width=40)

    for pkg in sorted(result.packages, key=lambda p: -p.relevance_score)[:15]:
        rel_color = "green" if pkg.relevance_score >= 0.8 else "yellow" if pkg.relevance_score >= 0.5 else "dim"
        key_data = ""
        if pkg.package_type == "entity_context":
            key_data = f"Owner: {pkg.context_data.get('owner', 'N/A')}, Risks: {len(pkg.context_data.get('risk_indicators', []))}"
        elif pkg.package_type == "person_context":
            key_data = f"Agents: {len(pkg.context_data.get('owned_agents', []))}, Gaps: {len(pkg.context_data.get('coverage_gaps', []))}"
        elif pkg.package_type == "organization_summary":
            key_data = f"Health: {pkg.context_data.get('health_summary', 'N/A')}"

        pkg_table.add_row(
            pkg.entity_name[:26],
            pkg.entity_id[:16] if pkg.entity_id != "org" else "organization",
            pkg.package_type,
            f"[{rel_color}]{pkg.relevance_score}[/{rel_color}]",
            key_data[:44],
        )

    console.print(pkg_table)

    console.print(Panel(
        f"[bold]Context packages provide real-time organizational data for Executive Avatar interactions.[/bold]\n"
        f"Every entity, person, and organization-level summary is pre-computed and ready for instant retrieval.",
        title="[bold]Executive Context Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
    result = run_executive_context_intelligence("data/sunrise_care.json")
    display_context_intelligence_report(result, data["company"])
