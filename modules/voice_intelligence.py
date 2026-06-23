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
class VoiceCommand:
    raw_input: str
    parsed_intent: str
    entities: list[str]
    parameters: dict[str, Any]
    response: str
    confidence: float
    execution_time_ms: int


@dataclass
class VoiceSessionMetrics:
    total_commands: int
    successful_parses: int
    failed_parses: int
    avg_confidence: float
    intent_distribution: dict[str, int]
    entity_resolution_rate: float


VOICE_INTENTS = {
    "query_risk": {
        "patterns": ["what is the risk", "show me risks", "how risky", "risk level of", "analyze risk"],
        "entity_required": False,
        "response_template": "Risk analysis for {entity}: {risk_details}",
    },
    "query_owner": {
        "patterns": ["who owns", "who is responsible for", "who manages", "owner of"],
        "entity_required": True,
        "response_template": "{entity} is owned by {owner}.",
    },
    "query_health": {
        "patterns": ["how healthy", "organization health", "health score", "overall status"],
        "entity_required": False,
        "response_template": "Organization health: {health_score}.",
    },
    "query_dependencies": {
        "patterns": ["what depends on", "dependencies of", "what breaks if", "cascade from"],
        "entity_required": True,
        "response_template": "{entity} has {dep_count} dependencies.",
    },
    "simulate_departure": {
        "patterns": ["what if", "simulate", "if someone leaves", "departure impact"],
        "entity_required": True,
        "response_template": "If {entity} leaves: {impact}.",
    },
    "recommend_action": {
        "patterns": ["what should we do", "recommend", "next steps", "priority actions"],
        "entity_required": False,
        "response_template": "Top recommendations: {recommendations}.",
    },
    "list_assets": {
        "patterns": ["list all", "show me all", "what agents", "what tools", "what workflows"],
        "entity_required": False,
        "response_template": "Found {count} {asset_type} assets.",
    },
    "compare_entities": {
        "patterns": ["compare", "versus", "vs", "difference between"],
        "entity_required": True,
        "response_template": "Comparison: {comparison}.",
    },
}


def parse_voice_command(raw_input: str, context: ContextIntelligenceResult) -> VoiceCommand:
    raw_lower = raw_input.lower()

    best_intent = "general_query"
    best_score = 0

    for intent, config in VOICE_INTENTS.items():
        score = sum(1 for p in config["patterns"] if p in raw_lower)
        if score > best_score:
            best_score = score
            best_intent = intent

    entities = []
    for vm in context.voice_models:
        for alias in vm.aliases:
            if alias in raw_lower:
                entities.append(vm.entity_name)
                break

    confidence = min(0.95, 0.3 + best_score * 0.2)
    if entities:
        confidence = min(0.95, confidence + 0.1)

    response = _generate_voice_response(best_intent, entities, context)

    return VoiceCommand(
        raw_input=raw_input,
        parsed_intent=best_intent,
        entities=entities,
        parameters={},
        response=response,
        confidence=round(confidence, 2),
        execution_time_ms=0,
    )


def _generate_voice_response(intent: str, entities: list[str], context: ContextIntelligenceResult) -> str:
    org = context.organization_context

    if intent == "query_risk":
        if entities:
            e_ctx = [e for e in context.entity_contexts if e.entity_name in entities]
            if e_ctx:
                e = e_ctx[0]
                return f"{e.entity_name}: criticality {e.criticality}, {len(e.risk_indicators)} risks detected."
        return f"Organization: {org.health_summary}. {len(org.critical_assets)} critical assets."

    elif intent == "query_owner":
        if entities:
            e_ctx = [e for e in context.entity_contexts if e.entity_name in entities]
            if e_ctx:
                return f"{e_ctx[0].entity_name} is owned by {e_ctx[0].owner or 'no one'}."
        return "Please specify which asset you want to look up."

    elif intent == "query_health":
        return f"Health: {org.health_summary}. {len(org.orphaned_assets)} orphaned, {len(org.undocumented_assets)} undocumented."

    elif intent == "query_dependencies":
        if entities:
            e_ctx = [e for e in context.entity_contexts if e.entity_name in entities]
            if e_ctx:
                return f"{e_ctx[0].entity_name}: {len(e_ctx[0].related_entities)} relationships."
        return f"Total relationships in graph: {org.total_relationships}."

    elif intent == "simulate_departure":
        if entities:
            p_ctx = [p for p in context.person_contexts if p.person_name in entities]
            if p_ctx:
                p = p_ctx[0]
                return f"If {p.person_name} leaves: {len(p.owned_agents)} agents affected, {len(p.coverage_gaps)} gaps."
        return "Specify a person or asset to simulate."

    elif intent == "recommend_action":
        recs = []
        if org.orphaned_assets:
            recs.append(f"Assign owners to {', '.join(org.orphaned_assets[:2])}")
        if org.undocumented_assets:
            recs.append(f"Document {len(org.undocumented_assets)} assets")
        return " | ".join(recs) if recs else "No urgent actions needed."

    elif intent == "list_assets":
        counts = org.entity_type_counts
        parts = [f"{count} {etype}" for etype, count in counts.items()]
        return f"Assets: {', '.join(parts)}."

    elif intent == "compare_entities":
        if len(entities) >= 2:
            e1 = next((e for e in context.entity_contexts if e.entity_name == entities[0]), None)
            e2 = next((e for e in context.entity_contexts if e.entity_name == entities[1]), None)
            if e1 and e2:
                return f"{e1.entity_name} ({e1.entity_type}, {e1.criticality}) vs {e2.entity_name} ({e2.entity_type}, {e2.criticality})."
        return "Please specify two entities to compare."

    return f"{org.company}: {org.total_entities} entities, health {org.health_summary}."


def run_voice_intelligence(data_path: str) -> tuple[list[VoiceCommand], VoiceSessionMetrics]:
    with open(data_path) as f:
        data = json.load(f)

    context = run_context_intelligence(data_path)

    sample_commands = [
        "What are the top risks in the organization?",
        "Who owns the Payroll Agent?",
        "How healthy is our AI infrastructure?",
        "What happens if the Onboarding Agent fails?",
        "What should we fix first?",
        "Show me all agents in the system",
        "Compare Robert and Lisa",
        "What dependencies does ChatGPT have?",
        "Simulate Robert leaving the company",
        "List all critical assets",
    ]

    commands = []
    intent_dist = {}
    total_confidence = 0
    successful = 0
    entities_found = 0
    total_entities_attempted = 0

    for raw in sample_commands:
        cmd = parse_voice_command(raw, context)
        commands.append(cmd)

        intent_dist[cmd.parsed_intent] = intent_dist.get(cmd.parsed_intent, 0) + 1
        total_confidence += cmd.confidence

        if cmd.confidence >= 0.5:
            successful += 1

        if cmd.entities:
            entities_found += len(cmd.entities)
            total_entities_attempted += 1

    metrics = VoiceSessionMetrics(
        total_commands=len(sample_commands),
        successful_parses=successful,
        failed_parses=len(sample_commands) - successful,
        avg_confidence=round(total_confidence / len(sample_commands), 2),
        intent_distribution=intent_dist,
        entity_resolution_rate=round(entities_found / max(total_entities_attempted, 1), 2),
    )

    storage = IntelligenceStorage()
    storage.save_analysis("voice_intelligence", {
        "company": data["company"],
        "total_commands": metrics.total_commands,
        "avg_confidence": metrics.avg_confidence,
        "entity_resolution_rate": metrics.entity_resolution_rate,
    })

    return commands, metrics


def display_voice_report(commands: list[VoiceCommand], metrics: VoiceSessionMetrics, company: str):
    console.print(Panel(
        f"[bold cyan]MODULE 22 — VOICE INTELLIGENCE ENGINE[/bold cyan]\n[dim]{company}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Commands Processed:[/bold] {metrics.total_commands}\n"
        f"[bold]Successful Parses:[/bold] {metrics.successful_parses}\n"
        f"[bold]Average Confidence:[/bold] {metrics.avg_confidence}\n"
        f"[bold]Entity Resolution Rate:[/bold] {metrics.entity_resolution_rate}",
        title="[bold]Session Metrics[/bold]",
        box=box.ROUNDED,
    ))

    console.print("\n[bold]Intent Distribution:[/bold]")
    for intent, count in sorted(metrics.intent_distribution.items(), key=lambda x: -x[1]):
        bar = "#" * (count * 3)
        console.print(f"  [cyan]{intent}[/cyan]: {bar} ({count})")

    console.print(Panel("[bold cyan]VOICE COMMAND PROCESSING LOG[/bold cyan]", box=box.SIMPLE))

    cmd_table = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    cmd_table.add_column("Input", style="white", min_width=32)
    cmd_table.add_column("Intent", min_width=18)
    cmd_table.add_column("Entities", min_width=16)
    cmd_table.add_column("Conf.", justify="center", min_width=6)
    cmd_table.add_column("Response", min_width=40)

    for cmd in commands:
        conf_color = "green" if cmd.confidence >= 0.7 else "yellow" if cmd.confidence >= 0.5 else "red"
        entities_str = ", ".join(cmd.entities) if cmd.entities else "[dim]none[/dim]"

        cmd_table.add_row(
            cmd.raw_input[:35],
            cmd.parsed_intent,
            entities_str[:18],
            f"[{conf_color}]{cmd.confidence}[/{conf_color}]",
            cmd.response[:45],
        )

    console.print(cmd_table)

    console.print(Panel(
        f"[bold]Voice Intelligence Engine processes natural language queries.[/bold]\n"
        f"Parses intent, resolves entities, generates contextual responses.",
        title="[bold]Voice Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
    commands, metrics = run_voice_intelligence("data/sunrise_care.json")
    display_voice_report(commands, metrics, data["company"])
