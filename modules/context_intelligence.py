import io
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box

from modules.ontology_layer import build_ontology, OntologyRegistry, OntologyEntity
from modules.relationship_layer import build_relationship_graph, RelationshipGraph
from modules.storage_layer import IntelligenceStorage

if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)


@dataclass
class EntityContext:
    entity_id: str
    entity_name: str
    entity_type: str
    properties: dict[str, Any]
    owner: Optional[str]
    department: Optional[str]
    criticality: str
    documented: bool
    related_entities: list[dict]
    risk_indicators: list[str]
    governance_status: str
    summary: str


@dataclass
class PersonContext:
    person_id: str
    person_name: str
    owned_agents: list[str]
    owned_workflows: list[str]
    backup_for: list[str]
    tools_used: list[str]
    departments: list[str]
    total_responsibilities: int
    coverage_gaps: list[str]
    risk_level: str
    summary: str


@dataclass
class OrganizationContext:
    company: str
    total_entities: int
    total_relationships: int
    entity_type_counts: dict[str, int]
    critical_assets: list[str]
    orphaned_assets: list[str]
    undocumented_assets: list[str]
    top_risks: list[str]
    health_summary: str
    executive_brief: str


@dataclass
class VoiceEntityModel:
    entity_id: str
    entity_name: str
    entity_type: str
    aliases: list[str]
    semantic_description: str
    related_concepts: list[str]
    conversational_triggers: list[str]
    context_summary: str


@dataclass
class VoiceContextPackage:
    intent_understanding: list[dict]
    entity_resolution: dict[str, str]
    relationship_narratives: list[str]
    risk_narratives: list[str]
    organizational_summary: str


@dataclass
class ContextIntelligenceResult:
    organization_context: OrganizationContext
    entity_contexts: list[EntityContext]
    person_contexts: list[PersonContext]
    voice_models: list[VoiceEntityModel]
    voice_context: VoiceContextPackage


RISK_KEYWORDS = {
    "orphaned": ["no owner", "orphaned", "unmanaged"],
    "undocumented": ["not documented", "no documentation", "undocumented"],
    "single_point": ["single point of failure", "spof", "sole"],
    "concentration": ["concentration", "too many", "overloaded"],
    "cascade": ["cascade", "chain reaction", "breaks downstream"],
    "expired": ["expired", "outdated", "needs review"],
}

RISK_LABELS = {
    "orphaned": "Orphaned Asset",
    "undocumented": "Documentation Gap",
    "single_point": "Single Point of Failure",
    "concentration": "Concentration Risk",
    "cascade": "Cascade Risk",
    "expired": "Policy Expiry Risk",
}


def build_entity_context(
    entity: OntologyEntity,
    graph: RelationshipGraph,
    registry: OntologyRegistry,
) -> EntityContext:
    related = []
    risk_indicators = []

    node = graph.nodes.get(entity.id)
    if node:
        for edge in graph.adjacency.get(entity.id, []):
            target = graph.nodes.get(edge.target_id)
            if target:
                related.append({
                    "name": target.name,
                    "type": target.entity_type,
                    "relationship": edge.relationship_type,
                    "direction": "outgoing",
                })

        for edge in graph.reverse_adjacency.get(entity.id, []):
            source = graph.nodes.get(edge.source_id)
            if source:
                related.append({
                    "name": source.name,
                    "type": source.entity_type,
                    "relationship": edge.relationship_type,
                    "direction": "incoming",
                })

    owner = entity.properties.get("owner") or entity.properties.get("access_owner") or entity.properties.get("created_by")
    if not owner and entity.entity_type in ("agent", "workflow"):
        risk_indicators.append("No owner assigned")

    if not entity.properties.get("documented"):
        risk_indicators.append("Not documented")

    backup = entity.properties.get("backup_owner") or entity.properties.get("backup_tool")
    if not backup and entity.entity_type in ("agent", "workflow", "system"):
        if entity.properties.get("criticality") in ("critical", "high"):
            risk_indicators.append("Critical asset without backup")

    if entity.entity_type == "agent":
        incoming = graph.reverse_adjacency.get(entity.id, [])
        if len(incoming) >= 3:
            risk_indicators.append(f"High dependency load ({len(incoming)} incoming)")

    crit = entity.properties.get("criticality", "medium")
    if crit == "critical":
        risk_indicators.append("Criticality: CRITICAL")

    if entity.entity_type == "knowledge":
        status = entity.properties.get("status")
        if status == "expired":
            risk_indicators.append("Governance policy expired")
        elif status == "draft":
            risk_indicators.append("Policy still in draft")

    governance_status = "GOVERNED"
    if entity.entity_type in ("agent", "workflow", "system"):
        policies = [
            r for r in registry.relationships
            if r.target_id == entity.id and r.relationship_type == "governs"
        ]
        if not policies:
            governance_status = "NO GOVERNANCE"
        else:
            active_policies = []
            for p in policies:
                policy_entity = registry.entities.get(p.source_id)
                if policy_entity and policy_entity.properties.get("status") in ("active", "enforced"):
                    active_policies.append(policy_entity)
            if not active_policies:
                governance_status = "EXPIRED/DRAFT POLICIES"

    if entity.entity_type == "human":
        summary = f"{entity.name} is a person"
        if entity.properties.get("department"):
            summary += f" in {entity.properties['department']}"
        summary += f" with {len(related)} relationships in the organization."
    elif entity.entity_type == "agent":
        summary = f"{entity.name} is an AI agent"
        if owner:
            summary += f" owned by {owner}"
        summary += f" with criticality {crit}."
        if risk_indicators:
            summary += f" Risks: {', '.join(risk_indicators)}."
    elif entity.entity_type == "system":
        summary = f"{entity.name} is an AI tool"
        vendor = entity.properties.get("vendor")
        if vendor:
            summary += f" by {vendor}"
        users = entity.properties.get("users", [])
        summary += f" used by {len(users)} people."
    elif entity.entity_type == "workflow":
        summary = f"{entity.name} is a business workflow"
        if owner:
            summary += f" owned by {owner}"
        steps = entity.properties.get("steps", [])
        summary += f" with {len(steps)} steps."
    elif entity.entity_type == "knowledge":
        summary = f"{entity.name} is a governance policy"
        domain = entity.properties.get("domain")
        if domain:
            summary += f" in the {domain} domain"
        summary += f" with status {entity.properties.get('status', 'unknown')}."
    else:
        summary = f"{entity.name} is a {entity.entity_type} entity."

    return EntityContext(
        entity_id=entity.id,
        entity_name=entity.name,
        entity_type=entity.entity_type,
        properties=entity.properties,
        owner=owner,
        department=entity.properties.get("department"),
        criticality=crit,
        documented=entity.properties.get("documented", False),
        related_entities=related,
        risk_indicators=risk_indicators,
        governance_status=governance_status,
        summary=summary,
    )


def build_person_context(
    person: OntologyEntity,
    registry: OntologyRegistry,
    graph: RelationshipGraph,
) -> PersonContext:
    owned_agents = []
    owned_workflows = []
    backup_for = []
    tools_used = []
    departments = set()
    coverage_gaps = []

    for rel in registry.relationships:
        if rel.source_id == person.id and rel.relationship_type == "owns":
            target = registry.entities.get(rel.target_id)
            if target:
                role = rel.metadata.get("role", "primary_owner")
                if target.entity_type == "agent":
                    if role == "backup_owner":
                        backup_for.append(target.name)
                    else:
                        owned_agents.append(target.name)
                elif target.entity_type == "workflow":
                    if role == "backup_owner":
                        backup_for.append(target.name)
                    else:
                        owned_workflows.append(target.name)

    for rel in registry.relationships:
        if rel.target_id == person.id and rel.relationship_type == "uses":
            source = registry.entities.get(rel.source_id)
            if source and source.entity_type == "system":
                tools_used.append(source.name)

    for agent_id in owned_agents:
        agent_entity = None
        for e in registry.entities.values():
            if e.name == agent_id and e.entity_type == "agent":
                agent_entity = e
                break
        if agent_entity:
            if agent_entity.properties.get("department"):
                departments.add(agent_entity.properties["department"])
            if not agent_entity.properties.get("backup_owner"):
                coverage_gaps.append(f"{agent_id} has no backup owner")

    total = len(owned_agents) + len(owned_workflows) + len(backup_for)

    risk_level = "LOW"
    if total == 0:
        risk_level = "NONE"
    elif len(owned_agents) >= 4:
        risk_level = "CRITICAL"
    elif len(owned_agents) >= 3:
        risk_level = "HIGH"
    elif len(coverage_gaps) > 0:
        risk_level = "MEDIUM"

    summary = f"{person.name} owns {len(owned_agents)} agents and {len(owned_workflows)} workflows."
    if backup_for:
        summary += f" Backup for {len(backup_for)} assets."
    if coverage_gaps:
        summary += f" {len(coverage_gaps)} coverage gaps."
    if risk_level in ("CRITICAL", "HIGH"):
        summary += f" Risk level: {risk_level}."

    return PersonContext(
        person_id=person.id,
        person_name=person.name,
        owned_agents=owned_agents,
        owned_workflows=owned_workflows,
        backup_for=backup_for,
        tools_used=tools_used,
        departments=sorted(departments),
        total_responsibilities=total,
        coverage_gaps=coverage_gaps,
        risk_level=risk_level,
        summary=summary,
    )


def build_organization_context(
    data: dict,
    registry: OntologyRegistry,
    entity_contexts: list[EntityContext],
    person_contexts: list[PersonContext],
) -> OrganizationContext:
    type_counts = {}
    for e in registry.entities.values():
        type_counts[e.entity_type] = type_counts.get(e.entity_type, 0) + 1

    critical_assets = [
        e.entity_name for e in entity_contexts
        if e.criticality == "critical"
    ]

    orphaned = [
        e.entity_name for e in entity_contexts
        if e.entity_type == "agent" and not e.owner
    ]

    undocumented = [
        e.entity_name for e in entity_contexts
        if not e.documented and e.entity_type in ("agent", "workflow", "system")
    ]

    top_risks = []
    for e in entity_contexts:
        for risk in e.risk_indicators:
            if "No owner" in risk:
                top_risks.append(f"{e.entity_name}: {risk}")
                break

    for p in person_contexts:
        if p.risk_level == "CRITICAL":
            top_risks.append(f"{p.person_name}: Human SPOF — {len(p.owned_agents)} agents, {len(p.coverage_gaps)} gaps")

    health_score = 100
    health_score -= len(orphaned) * 8
    health_score -= len(undocumented) * 3
    health_score -= len([p for p in person_contexts if p.risk_level == "CRITICAL"]) * 10
    health_score = max(0, health_score)

    if health_score >= 80:
        health_summary = "HEALTHY"
    elif health_score >= 60:
        health_summary = "WARNING"
    elif health_score >= 40:
        health_summary = "AT RISK"
    else:
        health_summary = "CRITICAL"

    brief = f"{data['company']} has {len(registry.entities)} entities and {len(registry.relationships)} relationships."
    brief += f" {len(orphaned)} orphaned assets, {len(undocumented)} undocumented."
    brief += f" Health: {health_score}/100 ({health_summary})."

    return OrganizationContext(
        company=data["company"],
        total_entities=len(registry.entities),
        total_relationships=len(registry.relationships),
        entity_type_counts=type_counts,
        critical_assets=critical_assets,
        orphaned_assets=orphaned,
        undocumented_assets=undocumented,
        top_risks=top_risks[:10],
        health_summary=f"{health_score}/100 — {health_summary}",
        executive_brief=brief,
    )


def build_voice_models(
    registry: OntologyRegistry,
    graph: RelationshipGraph,
) -> list[VoiceEntityModel]:
    models = []

    for entity in registry.entities.values():
        aliases = [entity.name.lower()]
        if entity.entity_type == "agent":
            words = entity.name.replace("Agent", "").strip().lower().split()
            aliases.extend(words)
        elif entity.entity_type == "system":
            aliases.append(entity.name.lower().replace(" ", ""))
        elif entity.entity_type == "human":
            first_name = entity.name.split()[0].lower() if entity.name else ""
            if first_name:
                aliases.append(first_name)

        related_concepts = []
        for rel in registry.relationships:
            if rel.source_id == entity.id:
                target = registry.entities.get(rel.target_id)
                if target:
                    related_concepts.append(f"{rel.relationship_type} {target.name}")
            elif rel.target_id == entity.id:
                source = registry.entities.get(rel.source_id)
                if source:
                    related_concepts.append(f"{source.name} {rel.relationship_type}")

        triggers = []
        if entity.entity_type == "agent":
            triggers.append(f"who owns {entity.name}")
            triggers.append(f"what does {entity.name} do")
            triggers.append(f"risk of {entity.name}")
        elif entity.entity_type == "human":
            triggers.append(f"what does {entity.name} own")
            triggers.append(f"dependencies of {entity.name}")
        elif entity.entity_type == "workflow":
            triggers.append(f"steps of {entity.name}")
            triggers.append(f"who runs {entity.name}")

        description = f"{entity.name} is a {entity.entity_type}"
        if entity.properties.get("criticality"):
            description += f" with {entity.properties['criticality']} criticality"

        models.append(VoiceEntityModel(
            entity_id=entity.id,
            entity_name=entity.name,
            entity_type=entity.entity_type,
            aliases=aliases,
            semantic_description=description,
            related_concepts=related_concepts[:5],
            conversational_triggers=triggers,
            context_summary=description,
        ))

    return models


def build_voice_context(
    data: dict,
    registry: OntologyRegistry,
    org_context: OrganizationContext,
) -> VoiceContextPackage:
    intents = [
        {"intent": "risk_assessment", "description": "User wants to understand organizational risks", "trigger_words": ["risk", "danger", "threat", "vulnerable"]},
        {"intent": "ownership_query", "description": "User wants to know who owns what", "trigger_words": ["owner", "responsible", "accountable", "who owns"]},
        {"intent": "dependency_analysis", "description": "User wants to understand dependencies", "trigger_words": ["depend", "break", "cascade", "impact"]},
        {"intent": "health_check", "description": "User wants organizational health status", "trigger_words": ["health", "score", "status", "overall"]},
        {"intent": "simulation", "description": "User wants to simulate disruption scenarios", "trigger_words": ["what if", "simulate", "scenario", "leaves"]},
        {"intent": "recommendation", "description": "User wants actionable recommendations", "trigger_words": ["recommend", "fix", "improve", "action"]},
    ]

    resolution = {}
    for entity in registry.entities.values():
        resolution[entity.name.lower()] = entity.id
        if entity.entity_type == "human":
            first = entity.name.split()[0].lower() if entity.name else ""
            if first:
                resolution[first] = entity.id

    narratives = []
    for rel_type, count in org_context.entity_type_counts.items():
        narratives.append(f"The organization has {count} {rel_type} entities.")

    risk_narratives = []
    if org_context.orphaned_assets:
        risk_narratives.append(f"{len(org_context.orphaned_assets)} assets have no owner: {', '.join(org_context.orphaned_assets[:3])}")
    if org_context.undocumented_assets:
        risk_narratives.append(f"{len(org_context.undocumented_assets)} assets lack documentation")

    return VoiceContextPackage(
        intent_understanding=intents,
        entity_resolution=resolution,
        relationship_narratives=narratives,
        risk_narratives=risk_narratives,
        organizational_summary=org_context.executive_brief,
    )


def run_context_intelligence(data_path: str) -> ContextIntelligenceResult:
    with open(data_path) as f:
        data = json.load(f)

    registry = build_ontology(data)
    graph = build_relationship_graph(registry)

    entity_contexts = []
    for entity in registry.entities.values():
        ctx = build_entity_context(entity, graph, registry)
        entity_contexts.append(ctx)

    person_contexts = []
    for person in registry.get_entities_by_type("human"):
        ctx = build_person_context(person, registry, graph)
        person_contexts.append(ctx)

    org_context = build_organization_context(data, registry, entity_contexts, person_contexts)
    voice_models = build_voice_models(registry, graph)
    voice_context = build_voice_context(data, registry, org_context)

    storage = IntelligenceStorage()
    storage.save_analysis("context", {
        "company": data["company"],
        "total_entities": org_context.total_entities,
        "total_relationships": org_context.total_relationships,
        "health_summary": org_context.health_summary,
        "orphaned_count": len(org_context.orphaned_assets),
        "undocumented_count": len(org_context.undocumented_assets),
        "critical_count": len(org_context.critical_assets),
        "voice_intents": len(voice_context.intent_understanding),
        "voice_entities": len(voice_models),
    })

    return ContextIntelligenceResult(
        organization_context=org_context,
        entity_contexts=entity_contexts,
        person_contexts=person_contexts,
        voice_models=voice_models,
        voice_context=voice_context,
    )


def display_context_report(result: ContextIntelligenceResult, company: str):
    org = result.organization_context

    console.print(Panel(
        f"[bold cyan]CONTEXT INTELLIGENCE LAYER + VOICE AGENT CONTEXT[/bold cyan]\n[dim]Company: {company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Total Entities:[/bold] {org.total_entities}\n"
        f"[bold]Total Relationships:[/bold] {org.total_relationships}\n"
        f"[bold]Critical Assets:[/bold] {len(org.critical_assets)}\n"
        f"[bold]Orphaned Assets:[/bold] {len(org.orphaned_assets)}\n"
        f"[bold]Undocumented Assets:[/bold] {len(org.undocumented_assets)}\n"
        f"[bold]Health:[/bold] {org.health_summary}\n\n"
        f"[bold]Executive Brief:[/bold] {org.executive_brief}",
        title="[bold]Organization Context[/bold]",
        box=box.ROUNDED,
    ))

    console.print(Panel("[bold cyan]ENTITY CONTEXT PACKAGES[/bold cyan]", box=box.SIMPLE))

    entity_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    entity_table.add_column("Entity", style="white", min_width=24)
    entity_table.add_column("Type", min_width=10)
    entity_table.add_column("Owner", min_width=12)
    entity_table.add_column("Criticality", justify="center", min_width=11)
    entity_table.add_column("Documented", justify="center", min_width=11)
    entity_table.add_column("Governance", min_width=16)
    entity_table.add_column("Risks", min_width=20)

    crit_colors = {"critical": "bold red", "high": "yellow", "medium": "blue", "low": "green"}

    for e in sorted(result.entity_contexts, key=lambda x: len(x.risk_indicators), reverse=True)[:20]:
        crit_color = crit_colors.get(e.criticality, "white")
        doc_text = "[green]YES[/green]" if e.documented else "[red]NO[/red]"
        risks = "; ".join(e.risk_indicators[:2]) if e.risk_indicators else "[green]None[/green]"

        entity_table.add_row(
            f"[bold]{e.entity_name}[/bold]",
            e.entity_type,
            e.owner or "[red]NONE[/red]",
            f"[{crit_color}]{e.criticality.upper()}[/{crit_color}]",
            doc_text,
            e.governance_status,
            risks[:40],
        )

    console.print(entity_table)

    console.print(Panel("[bold cyan]PERSON CONTEXT PACKAGES[/bold cyan]", box=box.SIMPLE))

    person_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    person_table.add_column("Person", style="white", min_width=14)
    person_table.add_column("Agents Owned", min_width=30)
    person_table.add_column("Workflows", min_width=24)
    person_table.add_column("Backup For", min_width=18)
    person_table.add_column("Coverage Gaps", min_width=20)
    person_table.add_column("Risk", justify="center", min_width=10)

    risk_colors = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green", "NONE": "dim"}

    for p in sorted(result.person_contexts, key=lambda x: x.total_responsibilities, reverse=True):
        risk_color = risk_colors.get(p.risk_level, "white")
        agents = ", ".join(p.owned_agents) if p.owned_agents else "[dim]none[/dim]"
        workflows = ", ".join(p.owned_workflows) if p.owned_workflows else "[dim]none[/dim]"
        backup = ", ".join(p.backup_for) if p.backup_for else "[dim]none[/dim]"
        gaps = "; ".join(p.coverage_gaps[:2]) if p.coverage_gaps else "[green]None[/green]"

        person_table.add_row(
            f"[bold]{p.person_name}[/bold]",
            agents[:35],
            workflows[:28],
            backup[:20],
            gaps[:24],
            f"[{risk_color}]{p.risk_level}[/{risk_color}]",
        )

    console.print(person_table)

    console.print(Panel("[bold cyan]VOICE AGENT CONTEXT LAYER[/bold cyan]", box=box.SIMPLE))

    console.print(f"\n[bold]Entity Resolution Map:[/bold] {len(result.voice_context.entity_resolution)} entries")
    console.print(f"[bold]Intent Definitions:[/bold] {len(result.voice_context.intent_understanding)} intents")
    console.print(f"[bold]Voice Entity Models:[/bold] {len(result.voice_models)} models")

    console.print("\n[bold]Intent Understanding:[/bold]")
    for intent in result.voice_context.intent_understanding:
        triggers = ", ".join(intent["trigger_words"][:4])
        console.print(f"  [cyan]{intent['intent']}[/cyan] — {intent['description']} [dim]({triggers})[/dim]")

    console.print("\n[bold]Sample Voice Entity Models:[/bold]")
    for vm in result.voice_models[:5]:
        console.print(f"  [bold]{vm.entity_name}[/bold] ({vm.entity_type})")
        console.print(f"    Aliases: {', '.join(vm.aliases[:3])}")
        console.print(f"    Triggers: {', '.join(vm.conversational_triggers[:2])}")

    console.print(Panel(
        f"[bold]Organization:[/bold] {org.company}\n"
        f"[bold]Entities:[/bold] {org.total_entities} | [bold]Relationships:[/bold] {org.total_relationships}\n"
        f"[bold]Critical:[/bold] {len(org.critical_assets)} | [bold]Orphaned:[/bold] {len(org.orphaned_assets)} | [bold]Undocumented:[/bold] {len(org.undocumented_assets)}\n"
        f"[bold]Health:[/bold] {org.health_summary}\n"
        f"[bold]Voice Models:[/bold] {len(result.voice_models)} | [bold]Intents:[/bold] {len(result.voice_context.intent_understanding)}",
        title="[bold]Context Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
    result = run_context_intelligence("data/sunrise_care.json")
    display_context_report(result, data["company"])
