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
class AvatarResponse:
    query: str
    intent: str
    entities_referenced: list[str]
    context_used: list[str]
    response_text: str
    confidence: float
    data_sources: list[str]


@dataclass
class AvatarSession:
    session_id: str
    organization: str
    queries_processed: int
    intents_breakdown: dict[str, int]
    avg_confidence: float
    sample_responses: list[AvatarResponse]


def detect_intent(query: str) -> tuple[str, float]:
    query_lower = query.lower()

    intent_signals = {
        "risk_assessment": ["risk", "danger", "threat", "vulnerable", "at risk", "critical", "exposed"],
        "ownership_query": ["owner", "responsible", "who owns", "accountable", "assigned to"],
        "dependency_analysis": ["depend", "break", "cascade", "impact", "if", "fails", "downstream"],
        "health_check": ["health", "score", "status", "overall", "how are we doing", "grade"],
        "simulation": ["what if", "simulate", "scenario", "leaves", "quits", "goes down"],
        "recommendation": ["recommend", "fix", "improve", "action", "should we", "next steps"],
        "governance": ["governance", "policy", "compliance", "audit", "regulation"],
        "accountability": ["accountability", "raci", "approval", "decision", "authority"],
    }

    best_intent = "general_query"
    best_score = 0.0

    for intent, signals in intent_signals.items():
        score = sum(1 for s in signals if s in query_lower)
        if score > best_score:
            best_score = score
            best_intent = intent

    confidence = min(0.95, 0.4 + best_score * 0.15)
    return best_intent, confidence


def extract_entities(query: str, context: ContextIntelligenceResult) -> list[str]:
    found = []
    query_lower = query.lower()

    for voice_model in context.voice_models:
        for alias in voice_model.aliases:
            if alias in query_lower:
                found.append(voice_model.entity_name)
                break

    return list(set(found))


def generate_response(
    query: str,
    intent: str,
    entities: list[str],
    context: ContextIntelligenceResult,
) -> str:
    org = context.organization_context

    if intent == "risk_assessment":
        if entities:
            entity_ctxs = [e for e in context.entity_contexts if e.entity_name in entities]
            if entity_ctxs:
                e = entity_ctxs[0]
                risks = ", ".join(e.risk_indicators) if e.risk_indicators else "none identified"
                return f"{e.entity_name} ({e.entity_type}) has criticality {e.criticality}. Risks: {risks}. Governance: {e.governance_status}."
        return f"Organization health: {org.health_summary}. {len(org.critical_assets)} critical assets, {len(org.orphaned_assets)} orphaned, {len(org.undocumented_assets)} undocumented."

    elif intent == "ownership_query":
        if entities:
            entity_ctxs = [e for e in context.entity_contexts if e.entity_name in entities]
            if entity_ctxs:
                e = entity_ctxs[0]
                owner = e.owner or "No owner assigned"
                return f"{e.entity_name} is owned by {owner}. Department: {e.department or 'N/A'}. Documented: {'yes' if e.documented else 'no'}."
        person_ctxs = [p for p in context.person_contexts if p.total_responsibilities > 0]
        return f"Key owners: {', '.join(p.person_name for p in person_ctxs[:3])}. {len(org.orphaned_assets)} assets have no owner."

    elif intent == "dependency_analysis":
        if entities:
            entity_ctxs = [e for e in context.entity_contexts if e.entity_name in entities]
            if entity_ctxs:
                e = entity_ctxs[0]
                incoming = [r for r in e.related_entities if r["direction"] == "incoming"]
                outgoing = [r for r in e.related_entities if r["direction"] == "outgoing"]
                return f"{e.entity_name} has {len(incoming)} incoming and {len(outgoing)} outgoing dependencies. If it fails, {len(outgoing)} downstream entities are affected."
        return f"Total relationships: {org.total_relationships}. {len(org.orphaned_assets)} entities disconnected from the graph."

    elif intent == "health_check":
        return f"Organizational Health: {org.health_summary}. Critical: {len(org.critical_assets)}, Orphaned: {len(org.orphaned_assets)}, Undocumented: {len(org.undocumented_assets)}."

    elif intent == "simulation":
        if entities:
            entity_ctxs = [e for e in context.entity_contexts if e.entity_name in entities]
            if entity_ctxs:
                e = entity_ctxs[0]
                return f"Simulating {e.entity_name} disruption: {len(e.related_entities)} entities would be impacted. This is a {e.criticality} criticality asset."
        person_ctxs = [p for p in context.person_contexts if p.risk_level in ("CRITICAL", "HIGH")]
        if person_ctxs:
            p = person_ctxs[0]
            return f"Highest risk departure: {p.person_name} — owns {len(p.owned_agents)} agents, {len(p.coverage_gaps)} coverage gaps."
        return "No high-risk disruption scenarios identified. Organization is stable."

    elif intent == "recommendation":
        recs = []
        if org.orphaned_assets:
            recs.append(f"Assign owners to: {', '.join(org.orphaned_assets[:3])}")
        if org.undocumented_assets:
            recs.append(f"Document: {', '.join(org.undocumented_assets[:3])}")
        critical_persons = [p for p in context.person_contexts if p.risk_level == "CRITICAL"]
        if critical_persons:
            recs.append(f"Redistribute workload from: {critical_persons[0].person_name}")
        return " | ".join(recs) if recs else "Organization is well-governed. No urgent recommendations."

    elif intent == "governance":
        governed = [e for e in context.entity_contexts if e.governance_status == "GOVERNED"]
        ungoverned = [e for e in context.entity_contexts if e.governance_status != "GOVERNED"]
        return f"Governance: {len(governed)} entities governed, {len(ungoverned)} with gaps."

    elif intent == "accountability":
        persons_with_coverage = [p for p in context.person_contexts if p.coverage_gaps]
        return f"Accountability gaps: {sum(len(p.coverage_gaps) for p in persons_with_coverage)} coverage gaps across {len(persons_with_coverage)} people."

    return f"{org.company}: {org.total_entities} entities, {org.total_relationships} relationships. Health: {org.health_summary}"


def run_executive_avatar(data_path: str) -> AvatarSession:
    with open(data_path) as f:
        data = json.load(f)

    context = run_context_intelligence(data_path)

    sample_queries = [
        "What are the biggest risks in the organization?",
        "Who owns the Lead Scoring Agent?",
        "What happens if Robert leaves?",
        "How healthy is our AI infrastructure?",
        "What should we fix first?",
        "Show me the dependency chain for Onboarding Agent",
        "Which agents are undocumented?",
        "What is the governance status of all agents?",
    ]

    responses = []
    intent_counts = {}
    total_confidence = 0

    for query in sample_queries:
        intent, confidence = detect_intent(query)
        entities = extract_entities(query, context)
        response_text = generate_response(query, intent, entities, context)

        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        total_confidence += confidence

        responses.append(AvatarResponse(
            query=query,
            intent=intent,
            entities_referenced=entities,
            context_used=["organization_context", "entity_contexts", "person_contexts"],
            response_text=response_text,
            confidence=round(confidence, 2),
            data_sources=["ontology", "relationship_graph", "context_intelligence"],
        ))

    session = AvatarSession(
        session_id="avatar_demo_001",
        organization=data["company"],
        queries_processed=len(sample_queries),
        intents_breakdown=intent_counts,
        avg_confidence=round(total_confidence / len(sample_queries), 2),
        sample_responses=responses,
    )

    storage = IntelligenceStorage()
    storage.save_analysis("executive_avatar", {
        "company": data["company"],
        "queries_processed": session.queries_processed,
        "avg_confidence": session.avg_confidence,
        "intents_breakdown": session.intents_breakdown,
    })

    return session


def display_avatar_report(session: AvatarSession):
    console.print(Panel(
        f"[bold cyan]MODULE 21 — EXECUTIVE AVATAR INTELLIGENCE[/bold cyan]\n[dim]{session.organization}[/dim]",
        box=box.DOUBLE,
    ))

    console.print(Panel(
        f"[bold]Queries Processed:[/bold] {session.queries_processed}\n"
        f"[bold]Average Confidence:[/bold] {session.avg_confidence}\n"
        f"[bold]Intents Detected:[/bold] {len(session.intents_breakdown)}",
        title="[bold]Avatar Session[/bold]",
        box=box.ROUNDED,
    ))

    console.print("\n[bold]Intent Distribution:[/bold]")
    for intent, count in sorted(session.intents_breakdown.items(), key=lambda x: -x[1]):
        bar = "#" * count
        console.print(f"  [cyan]{intent}[/cyan]: {bar} ({count})")

    console.print(Panel("[bold cyan]SAMPLE AVATAR RESPONSES[/bold cyan]", box=box.SIMPLE))

    for resp in session.sample_responses:
        conf_color = "green" if resp.confidence >= 0.7 else "yellow" if resp.confidence >= 0.5 else "red"
        console.print(f"\n[bold]Q:[/bold] {resp.query}")
        console.print(f"[bold]Intent:[/bold] {resp.intent} [{conf_color}]{resp.confidence}[/{conf_color}]")
        if resp.entities_referenced:
            console.print(f"[bold]Entities:[/bold] {', '.join(resp.entities_referenced)}")
        console.print(f"[bold]A:[/bold] {resp.response_text}")

    console.print(Panel(
        f"[bold]Executive Avatar is ready for real-time interaction.[/bold]\n"
        f"Processes queries, detects intent, resolves entities, generates contextual responses.",
        title="[bold]Avatar Intelligence Summary[/bold]",
        box=box.ROUNDED,
    ))


if __name__ == "__main__":
    with open("data/sunrise_care.json") as f:
        data = json.load(f)
    session = run_executive_avatar("data/sunrise_care.json")
    display_avatar_report(session)
