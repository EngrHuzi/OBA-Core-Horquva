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

from modules.intelligence_pipeline import IntelligencePipeline
from modules.storage_layer import IntelligenceStorage

if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

console = Console(file=sys.stdout, force_terminal=True, highlight=False)


@dataclass
class EntityType:
    name: str
    description: str
    required_properties: list[str]
    optional_properties: list[str]
    valid_relationships: list[str]
    constraints: list[str]


@dataclass
class RelationshipType:
    name: str
    description: str
    source_types: list[str]
    target_types: list[str]
    cardinality: str
    inverse: Optional[str] = None


@dataclass
class OntologyEntity:
    id: str
    name: str
    entity_type: str
    properties: dict[str, Any]
    relationships: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)


@dataclass
class OntologyRelationship:
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    relationship_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OntologySummary:
    total_entity_types: int
    total_relationship_types: int
    total_entities: int
    total_relationships: int
    entities_by_type: dict[str, int]
    relationships_by_type: dict[str, int]
    validation_errors: list[str]
    entity_type_definitions: list[dict]
    relationship_type_definitions: list[dict]


ENTITY_TYPES = {
    "human": EntityType(
        name="human",
        description="A person in the organization — employee, contractor, or stakeholder",
        required_properties=["name"],
        optional_properties=["department", "role", "email"],
        valid_relationships=["owns", "collaborates_with", "reports_to", "consulted_by"],
        constraints=[
            "A human can own zero or more agents",
            "A human can own zero or more workflows",
            "A human can be a backup owner for agents and workflows",
        ],
    ),
    "team": EntityType(
        name="team",
        description="A functional group of people organized around a business domain",
        required_properties=["name"],
        optional_properties=["department", "lead", "size"],
        valid_relationships=["contains", "collaborates_with", "governs"],
        constraints=[
            "A team contains one or more humans",
            "A team can own agents and workflows",
        ],
    ),
    "agent": EntityType(
        name="agent",
        description="An AI agent operating within the organization — performs automated tasks",
        required_properties=["name", "criticality"],
        optional_properties=["owner", "backup_owner", "department", "documented"],
        valid_relationships=["depends_on", "owned_by", "uses", "monitored_by", "governed_by"],
        constraints=[
            "An agent should have at least one owner",
            "An agent should have a backup owner for resilience",
            "An agent can depend on other agents, tools, or workflows",
        ],
    ),
    "system": EntityType(
        name="system",
        description="An AI tool, platform, or external system used by the organization",
        required_properties=["name", "criticality"],
        optional_properties=["vendor", "category", "users", "departments", "monthly_cost_usd", "backup_tool", "access_owner", "documented"],
        valid_relationships=["used_by", "depends_on", "backed_up_by", "governed_by"],
        constraints=[
            "A system should have an access owner",
            "Critical systems should have a backup tool defined",
        ],
    ),
    "workflow": EntityType(
        name="workflow",
        description="A business process — a sequence of steps involving humans, agents, and tools",
        required_properties=["name", "criticality"],
        optional_properties=["owner", "backup_owner", "department", "documented", "steps"],
        valid_relationships=["owned_by", "uses", "triggers", "governed_by"],
        constraints=[
            "A workflow should have at least one owner",
            "A workflow should be documented for recoverability",
        ],
    ),
    "knowledge": EntityType(
        name="knowledge",
        description="Organizational knowledge — policies, documentation, runbooks, institutional memory",
        required_properties=["name", "domain"],
        optional_properties=["status", "applies_to", "created_by", "compliance_required"],
        valid_relationships=["governs", "documented_by", "owned_by"],
        constraints=[
            "Knowledge should have a defined domain",
            "Compliance knowledge should be reviewed on a regular cycle",
        ],
    ),
}

RELATIONSHIP_TYPES = {
    "owns": RelationshipType(
        name="owns",
        description="A person has primary ownership and accountability for an entity",
        source_types=["human"],
        target_types=["agent", "workflow", "system", "knowledge"],
        cardinality="one-to-many",
        inverse="owned_by",
    ),
    "owned_by": RelationshipType(
        name="owned_by",
        description="An entity is owned and accountable to a person",
        source_types=["agent", "workflow", "system", "knowledge"],
        target_types=["human"],
        cardinality="many-to-one",
        inverse="owns",
    ),
    "depends_on": RelationshipType(
        name="depends_on",
        description="An entity requires another entity to function — failure of the target impacts the source",
        source_types=["agent", "system", "workflow"],
        target_types=["agent", "system", "workflow"],
        cardinality="many-to-many",
        inverse=" depended_on_by",
    ),
    "uses": RelationshipType(
        name="uses",
        description="A workflow or agent utilizes a system or tool to perform its function",
        source_types=["workflow", "agent"],
        target_types=["system"],
        cardinality="many-to-many",
        inverse="used_by",
    ),
    "monitors": RelationshipType(
        name="monitors",
        description="An entity observes or checks the health/status of another entity",
        source_types=["agent", "human"],
        target_types=["agent", "system", "workflow"],
        cardinality="one-to-many",
        inverse="monitored_by",
    ),
    "feeds": RelationshipType(
        name="feeds",
        description="An entity provides output or data that another entity consumes",
        source_types=["agent", "system", "workflow"],
        target_types=["agent", "system", "workflow"],
        cardinality="many-to-many",
        inverse="fed_by",
    ),
    "triggers": RelationshipType(
        name="triggers",
        description="An entity initiates or activates another entity's execution",
        source_types=["agent", "workflow", "human"],
        target_types=["agent", "workflow"],
        cardinality="one-to-many",
        inverse="triggered_by",
    ),
    "backs_up": RelationshipType(
        name="backs_up",
        description="An entity serves as a failover or redundancy for another entity",
        source_types=["agent", "human", "system"],
        target_types=["agent", "system", "workflow"],
        cardinality="many-to-one",
        inverse="backed_up_by",
    ),
    "governs": RelationshipType(
        name="governs",
        description="A knowledge entity (policy, rule, framework) applies governance to an entity",
        source_types=["knowledge"],
        target_types=["agent", "system", "workflow", "human"],
        cardinality="many-to-many",
        inverse="governed_by",
    ),
    "collaborates_with": RelationshipType(
        name="collaborates_with",
        description="Two entities work together on shared objectives",
        source_types=["human", "agent", "team"],
        target_types=["human", "agent", "team"],
        cardinality="many-to-many",
        inverse="collaborates_with",
    ),
    "sequential": RelationshipType(
        name="sequential",
        description="Two agents execute in sequence — the first must complete before the second starts",
        source_types=["agent"],
        target_types=["agent"],
        cardinality="many-to-many",
        inverse="preceded_by",
    ),
    "participates_in": RelationshipType(
        name="participates_in",
        description="A human or agent takes part in a workflow step",
        source_types=["human", "agent", "system"],
        target_types=["workflow"],
        cardinality="many-to-many",
        inverse="has_participant",
    ),
}


class OntologyRegistry:
    def __init__(self):
        self.entity_types: dict[str, EntityType] = {}
        self.relationship_types: dict[str, RelationshipType] = {}
        self.entities: dict[str, OntologyEntity] = {}
        self.relationships: list[OntologyRelationship] = []
        self._validation_errors: list[str] = []

    def register_entity_type(self, entity_type: EntityType):
        self.entity_types[entity_type.name] = entity_type

    def register_relationship_type(self, rel_type: RelationshipType):
        self.relationship_types[rel_type.name] = rel_type

    def add_entity(self, entity: OntologyEntity):
        self.entities[entity.id] = entity

    def add_relationship(self, relationship: OntologyRelationship):
        self.relationships.append(relationship)

    def validate_entity(self, entity: OntologyEntity) -> list[str]:
        errors = []
        etype = self.entity_types.get(entity.entity_type)
        if not etype:
            errors.append(f"Unknown entity type: {entity.entity_type}")
            return errors

        for prop in etype.required_properties:
            if prop not in entity.properties or entity.properties[prop] is None:
                errors.append(f"Missing required property: {prop}")

        return errors

    def validate_relationship(self, rel: OntologyRelationship) -> list[str]:
        errors = []
        rtype = self.relationship_types.get(rel.relationship_type)
        if not rtype:
            errors.append(f"Unknown relationship type: {rel.relationship_type}")
            return errors

        source = self.entities.get(rel.source_id)
        target = self.entities.get(rel.target_id)

        if not source:
            errors.append(f"Source entity not found: {rel.source_id}")
        elif source.entity_type not in rtype.source_types:
            errors.append(
                f"Source type mismatch: {source.entity_type} cannot be source of '{rel.relationship_type}' "
                f"(valid: {rtype.source_types})"
            )

        if not target:
            errors.append(f"Target entity not found: {rel.target_id}")
        elif target.entity_type not in rtype.target_types:
            errors.append(
                f"Target type mismatch: {target.entity_type} cannot be target of '{rel.relationship_type}' "
                f"(valid: {rtype.target_types})"
            )

        return errors

    def validate_all(self) -> list[str]:
        self._validation_errors = []
        for entity in self.entities.values():
            errors = self.validate_entity(entity)
            entity.validation_errors = errors
            self._validation_errors.extend(errors)
        for rel in self.relationships:
            errors = self.validate_relationship(rel)
            self._validation_errors.extend(errors)
        return self._validation_errors

    def get_entities_by_type(self, entity_type: str) -> list[OntologyEntity]:
        return [e for e in self.entities.values() if e.entity_type == entity_type]

    def get_relationships_for_entity(self, entity_id: str) -> list[OntologyRelationship]:
        return [r for r in self.relationships if r.source_id == entity_id or r.target_id == entity_id]

    def get_relationships_by_type(self, rel_type: str) -> list[OntologyRelationship]:
        return [r for r in self.relationships if r.relationship_type == rel_type]

    def get_ontology_summary(self) -> OntologySummary:
        entities_by_type: dict[str, int] = {}
        for e in self.entities.values():
            entities_by_type[e.entity_type] = entities_by_type.get(e.entity_type, 0) + 1

        relationships_by_type: dict[str, int] = {}
        for r in self.relationships:
            relationships_by_type[r.relationship_type] = relationships_by_type.get(r.relationship_type, 0) + 1

        entity_type_defs = []
        for name, etype in self.entity_types.items():
            entity_type_defs.append({
                "name": name,
                "description": etype.description,
                "required_properties": etype.required_properties,
                "optional_properties": etype.optional_properties,
                "valid_relationships": etype.valid_relationships,
                "constraints": etype.constraints,
                "count": entities_by_type.get(name, 0),
            })

        relationship_type_defs = []
        for name, rtype in self.relationship_types.items():
            relationship_type_defs.append({
                "name": name,
                "description": rtype.description,
                "source_types": rtype.source_types,
                "target_types": rtype.target_types,
                "cardinality": rtype.cardinality,
                "inverse": rtype.inverse,
                "count": relationships_by_type.get(name, 0),
            })

        return OntologySummary(
            total_entity_types=len(self.entity_types),
            total_relationship_types=len(self.relationship_types),
            total_entities=len(self.entities),
            total_relationships=len(self.relationships),
            entities_by_type=entities_by_type,
            relationships_by_type=relationships_by_type,
            validation_errors=self._validation_errors,
            entity_type_definitions=entity_type_defs,
            relationship_type_definitions=relationship_type_defs,
        )


def build_ontology(data: dict) -> OntologyRegistry:
    registry = OntologyRegistry()

    for etype in ENTITY_TYPES.values():
        registry.register_entity_type(etype)
    for rtype in RELATIONSHIP_TYPES.values():
        registry.register_relationship_type(rtype)

    people: set[str] = set()
    for agent in data.get("agents", []):
        if agent.get("owner"):
            people.add(agent["owner"])
        if agent.get("backup_owner"):
            people.add(agent["backup_owner"])
    for wf in data.get("workflows", []):
        if wf.get("owner"):
            people.add(wf["owner"])
        if wf.get("backup_owner"):
            people.add(wf["backup_owner"])
        for step in wf.get("steps", []):
            if step.get("actor") == "human":
                people.add(step["name"])
    for tool in data.get("ai_tools", []):
        if tool.get("access_owner"):
            people.add(tool["access_owner"])
        for user in tool.get("users", []):
            people.add(user)
    for policy in data.get("governance_policies", []):
        if policy.get("created_by"):
            people.add(policy["created_by"])

    for person in sorted(people):
        departments = set()
        for agent in data.get("agents", []):
            if agent.get("owner") == person or agent.get("backup_owner") == person:
                if agent.get("department"):
                    departments.add(agent["department"])
        for wf in data.get("workflows", []):
            if wf.get("owner") == person:
                if wf.get("department"):
                    departments.add(wf["department"])

        registry.add_entity(OntologyEntity(
            id=f"human_{person.lower().replace(' ', '_')}",
            name=person,
            entity_type="human",
            properties={
                "name": person,
                "department": ", ".join(sorted(departments)) if departments else None,
            },
        ))

    for agent in data.get("agents", []):
        registry.add_entity(OntologyEntity(
            id=agent["id"],
            name=agent["name"],
            entity_type="agent",
            properties={
                "name": agent["name"],
                "owner": agent.get("owner"),
                "backup_owner": agent.get("backup_owner"),
                "department": agent.get("department"),
                "criticality": agent.get("criticality", "medium"),
                "documented": agent.get("documented", False),
            },
        ))

    for tool in data.get("ai_tools", []):
        registry.add_entity(OntologyEntity(
            id=tool["id"],
            name=tool["name"],
            entity_type="system",
            properties={
                "name": tool["name"],
                "vendor": tool.get("vendor"),
                "category": tool.get("category"),
                "users": tool.get("users", []),
                "departments": tool.get("departments", []),
                "monthly_cost_usd": tool.get("monthly_cost_usd", 0),
                "criticality": tool.get("criticality", "medium"),
                "documented": tool.get("documented", False),
                "backup_tool": tool.get("backup_tool"),
                "access_owner": tool.get("access_owner"),
            },
        ))

    for wf in data.get("workflows", []):
        registry.add_entity(OntologyEntity(
            id=wf["id"],
            name=wf["name"],
            entity_type="workflow",
            properties={
                "name": wf["name"],
                "owner": wf.get("owner"),
                "backup_owner": wf.get("backup_owner"),
                "department": wf.get("department"),
                "criticality": wf.get("criticality", "medium"),
                "documented": wf.get("documented", False),
                "steps": wf.get("steps", []),
            },
        ))

    for policy in data.get("governance_policies", []):
        registry.add_entity(OntologyEntity(
            id=policy["id"],
            name=policy["name"],
            entity_type="knowledge",
            properties={
                "name": policy["name"],
                "domain": policy.get("domain"),
                "status": policy.get("status"),
                "applies_to": policy.get("applies_to", []),
                "created_by": policy.get("created_by"),
                "compliance_required": policy.get("compliance_required", False),
            },
        ))

    for agent in data.get("agents", []):
        if agent.get("owner"):
            owner_id = f"human_{agent['owner'].lower().replace(' ', '_')}"
            registry.add_relationship(OntologyRelationship(
                source_id=owner_id,
                source_name=agent["owner"],
                target_id=agent["id"],
                target_name=agent["name"],
                relationship_type="owns",
                metadata={"role": "primary_owner"},
            ))

        if agent.get("backup_owner"):
            backup_id = f"human_{agent['backup_owner'].lower().replace(' ', '_')}"
            registry.add_relationship(OntologyRelationship(
                source_id=backup_id,
                source_name=agent["backup_owner"],
                target_id=agent["id"],
                target_name=agent["name"],
                relationship_type="owns",
                metadata={"role": "backup_owner"},
            ))

    for dep in data.get("dependencies", []):
        rel_type = dep.get("type", "depends_on")
        if rel_type not in RELATIONSHIP_TYPES:
            rel_type = "depends_on"

        source_entity = registry.entities.get(dep["from"])
        target_entity = registry.entities.get(dep["to"])

        registry.add_relationship(OntologyRelationship(
            source_id=dep["from"],
            source_name=source_entity.name if source_entity else dep["from"],
            target_id=dep["to"],
            target_name=target_entity.name if target_entity else dep["to"],
            relationship_type=rel_type,
            metadata={"original_type": dep.get("type")},
        ))

    for tool in data.get("ai_tools", []):
        for agent_id in tool.get("agents_using", []):
            agent_entity = registry.entities.get(agent_id)
            if agent_entity:
                registry.add_relationship(OntologyRelationship(
                    source_id=agent_id,
                    source_name=agent_entity.name,
                    target_id=tool["id"],
                    target_name=tool["name"],
                    relationship_type="uses",
                ))

    for wf in data.get("workflows", []):
        for step in wf.get("steps", []):
            if step.get("actor") == "tool":
                tool_entities = [e for e in registry.entities.values() if e.entity_type == "system" and e.name == step["name"]]
                if tool_entities:
                    registry.add_relationship(OntologyRelationship(
                        source_id=wf["id"],
                        source_name=wf["name"],
                        target_id=tool_entities[0].id,
                        target_name=step["name"],
                        relationship_type="uses",
                        metadata={"step": step.get("step"), "action": step.get("action")},
                    ))

            elif step.get("actor") == "agent":
                registry.add_relationship(OntologyRelationship(
                    source_id=wf["id"],
                    source_name=wf["name"],
                    target_id=step["name"],
                    target_name=step["name"],
                    relationship_type="triggers",
                    metadata={"step": step.get("step"), "action": step.get("action")},
                ))

            elif step.get("actor") == "human":
                human_id = f"human_{step['name'].lower().replace(' ', '_')}"
                registry.add_relationship(OntologyRelationship(
                    source_id=human_id,
                    source_name=step["name"],
                    target_id=wf["id"],
                    target_name=wf["name"],
                    relationship_type="participates_in",
                    metadata={"step": step.get("step"), "action": step.get("action")},
                ))

    for policy in data.get("governance_policies", []):
        for target_id in policy.get("applies_to", []):
            target_entity = registry.entities.get(target_id)
            if target_entity:
                registry.add_relationship(OntologyRelationship(
                    source_id=policy["id"],
                    source_name=policy["name"],
                    target_id=target_id,
                    target_name=target_entity.name,
                    relationship_type="governs",
                ))

    registry.validate_all()
    return registry


@dataclass
class OntologyResult:
    summary: OntologySummary
    registry: OntologyRegistry


def run_ontology_intelligence(data_path: str) -> OntologyResult:
    with open(data_path) as f:
        data = json.load(f)

    registry = build_ontology(data)
    summary = registry.get_ontology_summary()

    storage = IntelligenceStorage()
    storage.save_analysis("ontology", {
        "company": data["company"],
        "total_entity_types": summary.total_entity_types,
        "total_relationship_types": summary.total_relationship_types,
        "total_entities": summary.total_entities,
        "total_relationships": summary.total_relationships,
        "entities_by_type": summary.entities_by_type,
        "relationships_by_type": summary.relationships_by_type,
        "validation_errors": summary.validation_errors,
    })

    return OntologyResult(summary=summary, registry=registry)


def display_ontology_report(result: OntologyResult, company: str):
    summary = result.summary
    registry = result.registry

    console.print(Panel(
        f"[bold cyan]ONTOLOGY LAYER — ORGANIZATIONAL BRAIN VOCABULARY[/bold cyan]\n[dim]Company: {company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Entity Types Defined:[/bold] {summary.total_entity_types}\n"
        f"[bold]Relationship Types Defined:[/bold] {summary.total_relationship_types}\n"
        f"[bold]Total Entities Registered:[/bold] {summary.total_entities}\n"
        f"[bold]Total Relationships Mapped:[/bold] {summary.total_relationships}\n"
        f"[bold]Validation Errors:[/bold] {len(summary.validation_errors)}",
        title="[bold]Ontology Summary[/bold]",
        box=box.ROUNDED,
    ))

    console.print(Panel("[bold cyan]ENTITY TYPE DEFINITIONS[/bold cyan]", box=box.SIMPLE))

    etype_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    etype_table.add_column("Type", style="white", min_width=12)
    etype_table.add_column("Description", min_width=40)
    etype_table.add_column("Required", min_width=24)
    etype_table.add_column("Optional", min_width=30)
    etype_table.add_column("Registered", justify="center", min_width=10)

    type_colors = {
        "human": "green",
        "team": "blue",
        "agent": "cyan",
        "system": "yellow",
        "workflow": "magenta",
        "knowledge": "red",
    }

    for etype_def in summary.entity_type_definitions:
        color = type_colors.get(etype_def["name"], "white")
        required = ", ".join(etype_def["required_properties"])
        optional = ", ".join(etype_def["optional_properties"]) if etype_def["optional_properties"] else "—"
        etype_table.add_row(
            f"[bold {color}]{etype_def['name'].upper()}[/]",
            etype_def["description"][:55] + ("..." if len(etype_def["description"]) > 55 else ""),
            required,
            optional,
            str(etype_def["count"]),
        )

    console.print(etype_table)

    console.print(Panel("[bold cyan]RELATIONSHIP TYPE DEFINITIONS[/bold cyan]", box=box.SIMPLE))

    rtype_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    rtype_table.add_column("Relationship", style="white", min_width=16)
    rtype_table.add_column("Description", min_width=40)
    rtype_table.add_column("Source Types", min_width=18)
    rtype_table.add_column("Target Types", min_width=18)
    rtype_table.add_column("Cardinality", min_width=14)
    rtype_table.add_column("Mapped", justify="center", min_width=8)

    for rtype_def in summary.relationship_type_definitions:
        rtype_table.add_row(
            f"[bold]{rtype_def['name']}[/bold]",
            rtype_def["description"][:50] + ("..." if len(rtype_def["description"]) > 50 else ""),
            ", ".join(rtype_def["source_types"]),
            ", ".join(rtype_def["target_types"]),
            rtype_def["cardinality"],
            str(rtype_def["count"]),
        )

    console.print(rtype_table)

    console.print(Panel("[bold cyan]ENTITY REGISTRY BY TYPE[/bold cyan]", box=box.SIMPLE))

    for etype_name, count in sorted(summary.entities_by_type.items()):
        entities = registry.get_entities_by_type(etype_name)
        color = type_colors.get(etype_name, "white")

        tree = Tree(f"[bold {color}]{etype_name.upper()}[/] — {count} entities")

        for entity in entities:
            rels = registry.get_relationships_for_entity(entity.id)
            rel_summary = f"{len(rels)} relationships"
            tree.add(f"[bold]{entity.name}[/bold] [dim]({entity.id})[/dim] — {rel_summary}")

        console.print(tree)

    console.print(Panel("[bold cyan]RELATIONSHIP MAP[/bold cyan]", box=box.SIMPLE))

    for rtype_name, count in sorted(summary.relationships_by_type.items()):
        if count == 0:
            continue
        rels = registry.get_relationships_by_type(rtype_name)

        rel_table = Table(box=box.ROUNDED, show_lines=False, title=f"[bold]{rtype_name}[/bold] ({count})")
        rel_table.add_column("Source", style="white", min_width=28)
        rel_table.add_column("->", justify="center", min_width=3)
        rel_table.add_column("Target", style="white", min_width=28)
        rel_table.add_column("Metadata", min_width=20)

        for rel in rels:
            meta_str = ""
            if rel.metadata:
                interesting = {k: v for k, v in rel.metadata.items() if k != "original_type"}
                if interesting:
                    meta_str = ", ".join(f"{k}={v}" for k, v in interesting.items())
            rel_table.add_row(
                f"{rel.source_name} [dim]({rel.source_id})[/dim]",
                "->",
                f"{rel.target_name} [dim]({rel.target_id})[/dim]",
                meta_str,
            )

        console.print(rel_table)

    if summary.validation_errors:
        console.print(Panel("[bold red]VALIDATION ERRORS[/bold red]", box=box.SIMPLE))
        for error in summary.validation_errors:
            console.print(f"  [red]•[/red] {error}")

    unowned = [e for e in registry.entities.values() if e.entity_type == "agent" and not e.properties.get("owner")]
    undocumented = [e for e in registry.entities.values() if e.entity_type in ("agent", "workflow") and not e.properties.get("documented")]
    no_backup = [e for e in registry.entities.values() if e.entity_type == "agent" and not e.properties.get("backup_owner")]

    console.print(Panel(
        f"[bold]Total Entity Types:[/bold] {summary.total_entity_types}\n"
        f"[bold]Total Relationship Types:[/bold] {summary.total_relationship_types}\n"
        f"[bold]Total Entities:[/bold] {summary.total_entities}\n"
        f"[bold]Total Relationships:[/bold] {summary.total_relationships}\n"
        f"[bold red]Orphaned Agents (no owner):[/bold red] {len(unowned)}\n"
        f"[bold red]Undocumented Assets:[/bold red] {len(undocumented)}\n"
        f"[bold yellow]Agents Without Backup:[/bold yellow] {len(no_backup)}\n"
        f"[bold green]Validation Errors:[/bold green] {len(summary.validation_errors)}\n\n"
        f"[bold]Ontology provides the single source of truth for all entity and relationship definitions.[/bold]",
        title="[bold]Ontology Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
    result = run_ontology_intelligence("data/sunrise_care.json")
    display_ontology_report(result, data["company"])
