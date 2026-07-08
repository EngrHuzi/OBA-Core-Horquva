from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime
from enum import Enum
import json
import os
import time

from modules.module_registry import (
    ModuleRegistry,
    ModulePhase,
    ModuleStatus,
    ModuleMetadata,
    get_registry,
)
from modules.capability_registry import (
    CapabilityRegistry,
    CapabilityType,
    DataType,
    get_capability_registry,
)
from modules.intelligence_exchange import (
    IntelligenceExchangeProtocol,
    MessageType,
    SignalType,
    MessagePriority,
    get_protocol,
)
from modules.knowledge_graph import (
    UnifiedKnowledgeGraph,
    GraphNodeType,
    GraphEdgeType,
    InsightSeverity,
    get_knowledge_graph,
    GraphNode,
    GraphEdge,
    GraphInsight,
)


class OrchestratorPhase(Enum):
    INITIALIZATION = "initialization"
    MODULE_DISCOVERY = "module_discovery"
    DEPENDENCY_RESOLUTION = "dependency_resolution"
    EXECUTION = "execution"
    AGGREGATION = "aggregation"
    COMPLETION = "completion"


class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DEPENDENCY_ORDER = "dependency_order"


@dataclass
class ExecutionResult:
    module_id: str
    success: bool
    execution_time_ms: float
    output: Any = None
    error: Optional[str] = None
    signals_emitted: int = 0
    insights_generated: int = 0


@dataclass
class PipelineResult:
    run_id: str
    started_at: str
    completed_at: Optional[str] = None
    phase: OrchestratorPhase = OrchestratorPhase.INITIALIZATION
    execution_mode: ExecutionMode = ExecutionMode.DEPENDENCY_ORDER
    total_modules: int = 0
    executed_modules: int = 0
    successful_modules: int = 0
    failed_modules: int = 0
    execution_results: list[ExecutionResult] = field(default_factory=list)
    total_signals: int = 0
    total_insights: int = 0
    total_time_ms: float = 0


class PlatformOrchestrator:
    _instance: Optional[PlatformOrchestrator] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.registry = get_registry()
        self.capability_registry = get_capability_registry()
        self.protocol = get_protocol()
        self.knowledge_graph = get_knowledge_graph()
        self._execution_order: list[str] = []
        self._initialized = True
    
    def initialize(self, data_path: str = "data/sunrise_care.json"):
        self._register_all_modules()
        self._register_capabilities()
        self._setup_protocol_handlers()
        self._build_knowledge_graph(data_path)
        
        self.registry.save("data/module_registry.json")
    
    def _register_all_modules(self):
        modules = [
            ("M01", "Ownership Intelligence", ModulePhase.CORE_INTELLIGENCE, "Analyzes AI agent ownership risk"),
            ("M02", "Dependency Intelligence", ModulePhase.CORE_INTELLIGENCE, "Maps agent dependency graphs"),
            ("M03", "Risk Intelligence", ModulePhase.CORE_INTELLIGENCE, "Calculates composite risk scores"),
            ("M04", "Recommendation Engine", ModulePhase.CORE_INTELLIGENCE, "Generates actionable recommendations"),
            ("M05", "What-If Simulation", ModulePhase.CORE_INTELLIGENCE, "Simulates disruption scenarios"),
            ("M06", "Human-Agent Map", ModulePhase.CORE_INTELLIGENCE, "Maps human-agent relationships"),
            ("M07", "AI Tool Intelligence", ModulePhase.CORE_INTELLIGENCE, "Audits AI tool usage and risk"),
            ("M08", "Workflow Intelligence", ModulePhase.CORE_INTELLIGENCE, "Maps business workflows"),
            ("M09", "Knowledge Risk Intelligence", ModulePhase.CORE_INTELLIGENCE, "Identifies knowledge concentration"),
            ("M10", "Organizational Memory", ModulePhase.CORE_INTELLIGENCE, "Tracks institutional memory"),
            ("M19", "Governance Intelligence", ModulePhase.GOVERNANCE_ACCOUNTABILITY, "Analyzes governance health"),
            ("M20", "Accountability Intelligence", ModulePhase.GOVERNANCE_ACCOUNTABILITY, "Maps accountability chains"),
            ("M21", "Executive Avatar", ModulePhase.EXECUTIVE_VOICE, "Processes executive queries"),
            ("M22", "Voice Intelligence", ModulePhase.EXECUTIVE_VOICE, "Processes voice commands"),
            ("M23", "Executive Briefing", ModulePhase.EXECUTIVE_VOICE, "Generates executive briefings"),
            ("M27", "Executive Context", ModulePhase.EXECUTIVE_VOICE, "Pre-computes context packages"),
            ("M28", "Universal Dependency Graph", ModulePhase.ORGANIZATIONAL_SCALE, "Maps all dependencies"),
            ("M29", "Org Relationship Intelligence", ModulePhase.ORGANIZATIONAL_SCALE, "Analyzes relationships"),
            ("M31", "Ecosystem Intelligence", ModulePhase.ORGANIZATIONAL_SCALE, "Maps organizational ecosystem"),
            ("M34", "Hidden Dependency Intelligence", ModulePhase.ORGANIZATIONAL_SCALE, "Surfaces hidden dependencies"),
            ("M35", "Network Intelligence", ModulePhase.ORGANIZATIONAL_SCALE, "Analyzes network behavior"),
            ("ONTOLOGY", "Ontology Layer", ModulePhase.ARCHITECTURE, "Defines entity vocabulary"),
            ("RELATIONSHIP", "Relationship Layer", ModulePhase.ARCHITECTURE, "Graph traversal and centrality"),
            ("CONTEXT", "Context Intelligence", ModulePhase.ARCHITECTURE, "Entity/person/org context"),
            ("VOICE_CTX", "Voice Agent Context", ModulePhase.ARCHITECTURE, "Voice models and intents"),
        ]
        
        for module_id, name, phase, description in modules:
            self.registry.register(ModuleMetadata(
                module_id=module_id,
                name=name,
                version="1.0.0",
                phase=phase,
                description=description,
                author="Horquva",
            ))
    
    def _register_capabilities(self):
        capabilities = [
            ("M01", "ownership_analysis", "Ownership Analysis", CapabilityType.PROCESS, "Analyze ownership risk"),
            ("M01", "ownership_output", "Ownership Results", CapabilityType.OUTPUT, "Ownership risk data"),
            ("M02", "dependency_analysis", "Dependency Analysis", CapabilityType.PROCESS, "Map dependencies"),
            ("M02", "dependency_output", "Dependency Graph", CapabilityType.OUTPUT, "Dependency relationships"),
            ("M03", "risk_scoring", "Risk Scoring", CapabilityType.PROCESS, "Calculate composite risk"),
            ("M03", "risk_output", "Risk Scores", CapabilityType.OUTPUT, "Risk assessments"),
            ("M04", "recommendation_generation", "Recommendation Generation", CapabilityType.PROCESS, "Generate recommendations"),
            ("M04", "recommendation_output", "Recommendations", CapabilityType.OUTPUT, "Actionable recommendations"),
            ("M05", "simulation", "What-If Simulation", CapabilityType.PROCESS, "Simulate scenarios"),
            ("M05", "simulation_output", "Simulation Results", CapabilityType.OUTPUT, "Scenario outcomes"),
            ("M19", "governance_analysis", "Governance Analysis", CapabilityType.PROCESS, "Analyze governance"),
            ("M19", "governance_output", "Governance Results", CapabilityType.OUTPUT, "Governance health data"),
            ("M20", "accountability_analysis", "Accountability Analysis", CapabilityType.PROCESS, "Map accountability"),
            ("M20", "accountability_output", "Accountability Results", CapabilityType.OUTPUT, "Accountability chains"),
            ("M28", "universal_dep_analysis", "Universal Dependency Analysis", CapabilityType.PROCESS, "Map all dependencies"),
            ("M28", "universal_dep_output", "Universal Dependency Graph", CapabilityType.OUTPUT, "Complete dependency graph"),
            ("M35", "network_analysis", "Network Analysis", CapabilityType.PROCESS, "Analyze network behavior"),
            ("M35", "network_output", "Network Results", CapabilityType.OUTPUT, "Network intelligence"),
        ]
        
        for module_id, cap_id, name, cap_type, desc in capabilities:
            self.capability_registry.register_capability(
                module_id=module_id,
                capability_id=cap_id,
                name=name,
                capability_type=cap_type,
                description=desc,
            )
    
    def _setup_protocol_handlers(self):
        def handle_risk_signal(message):
            self.knowledge_graph.add_node(GraphNode(
                node_id=f"risk_{message.payload.get('agent_id', 'unknown')}",
                node_type=GraphNodeType.RISK,
                name=f"Risk: {message.payload.get('agent_name', 'Unknown')}",
                properties=message.payload,
                source_module=message.source_module,
            ))
            return {"status": "processed"}
        
        self.protocol.register_handler(
            module_id="ORCHESTRATOR",
            message_type=MessageType.SIGNAL,
            callback=handle_risk_signal,
            filter_signal_type=SignalType.RISK_DETECTED,
        )
    
    def _build_knowledge_graph(self, data_path: str):
        with open(data_path) as f:
            data = json.load(f)
        
        for agent in data.get("agents", []):
            self.knowledge_graph.add_node(GraphNode(
                node_id=agent["id"],
                node_type=GraphNodeType.AGENT,
                name=agent["name"],
                properties=agent,
                source_module="DATA_LOAD",
            ))
            
            if agent.get("owner"):
                person_id = f"person_{agent['owner'].lower()}"
                self.knowledge_graph.add_node(GraphNode(
                    node_id=person_id,
                    node_type=GraphNodeType.PERSON,
                    name=agent["owner"],
                    source_module="DATA_LOAD",
                ))
                self.knowledge_graph.add_edge(GraphEdge(
                    edge_id=f"{agent['id']}_owns_{person_id}",
                    source_id=person_id,
                    target_id=agent["id"],
                    edge_type=GraphEdgeType.OWNS,
                    source_module="DATA_LOAD",
                ))
        
        for tool in data.get("ai_tools", []):
            self.knowledge_graph.add_node(GraphNode(
                node_id=tool["id"],
                node_type=GraphNodeType.TOOL,
                name=tool["name"],
                properties=tool,
                source_module="DATA_LOAD",
            ))
        
        for workflow in data.get("workflows", []):
            self.knowledge_graph.add_node(GraphNode(
                node_id=workflow["id"],
                node_type=GraphNodeType.WORKFLOW,
                name=workflow["name"],
                properties=workflow,
                source_module="DATA_LOAD",
            ))
        
        for policy in data.get("governance_policies", []):
            self.knowledge_graph.add_node(GraphNode(
                node_id=policy["id"],
                node_type=GraphNodeType.POLICY,
                name=policy["name"],
                properties=policy,
                source_module="DATA_LOAD",
            ))
    
    def run_pipeline(
        self,
        data_path: str = "data/sunrise_care.json",
        execution_mode: ExecutionMode = ExecutionMode.DEPENDENCY_ORDER,
    ) -> PipelineResult:
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = PipelineResult(
            run_id=run_id,
            started_at=datetime.now().isoformat(),
            execution_mode=execution_mode,
        )
        
        self.registry.update_status("ORCHESTRATOR", ModuleStatus.ACTIVE)
        
        order = self._get_execution_order(execution_mode)
        result.total_modules = len(order)
        
        for module_id in order:
            module_reg = self.registry.get(module_id)
            if not module_reg:
                continue
            
            self.registry.update_status(module_id, ModuleStatus.EXECUTING)
            start_time = time.time()
            
            try:
                if module_reg.run_function:
                    output = module_reg.run_function(data_path)
                    execution_time = (time.time() - start_time) * 1000
                    
                    exec_result = ExecutionResult(
                        module_id=module_id,
                        success=True,
                        execution_time_ms=execution_time,
                        output=output,
                    )
                    
                    self.registry.update_status(module_id, ModuleStatus.COMPLETED)
                    self.registry.update_execution_time(module_id, execution_time)
                    
                    self._emit_module_signals(module_id, output)
                    self._generate_module_insights(module_id, output)
                    
                    result.successful_modules += 1
                else:
                    exec_result = ExecutionResult(
                        module_id=module_id,
                        success=True,
                        execution_time_ms=0,
                        output=None,
                    )
                    result.successful_modules += 1
                
                result.execution_results.append(exec_result)
                result.executed_modules += 1
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                exec_result = ExecutionResult(
                    module_id=module_id,
                    success=False,
                    execution_time_ms=execution_time,
                    error=str(e),
                )
                result.execution_results.append(exec_result)
                result.failed_modules += 1
                self.registry.update_error(module_id, str(e))
        
        result.completed_at = datetime.now().isoformat()
        result.total_time_ms = sum(r.execution_time_ms for r in result.execution_results)
        result.total_signals = len(self.protocol.get_message_log())
        result.total_insights = len(self.knowledge_graph.get_insights())
        
        self.registry.update_status("ORCHESTRATOR", ModuleStatus.COMPLETED)
        self.registry.save("data/module_registry.json")
        self.knowledge_graph.save("data/knowledge_graph.json")
        
        return result
    
    def _get_execution_order(self, mode: ExecutionMode) -> list[str]:
        if mode == ExecutionMode.SEQUENTIAL:
            return self.registry.get_dependency_order()
        elif mode == ExecutionMode.DEPENDENCY_ORDER:
            return self.registry.get_dependency_order()
        else:
            return [reg.metadata.module_id for reg in self.registry.get_all()]
    
    def _emit_module_signals(self, module_id: str, output: Any):
        if output is None:
            return
        
        if isinstance(output, dict):
            if "risk_level" in output:
                self.protocol.emit_signal(
                    source_module=module_id,
                    signal_type=SignalType.RISK_DETECTED,
                    payload={"module_id": module_id, **output},
                )
            
            if "health_score" in output:
                self.protocol.emit_signal(
                    source_module=module_id,
                    signal_type=SignalType.HEALTH_SCORE_CHANGED,
                    payload={"module_id": module_id, **output},
                )
        
        elif isinstance(output, list):
            for item in output[:5]:
                if isinstance(item, dict) and "risk_level" in item:
                    self.protocol.emit_signal(
                        source_module=module_id,
                        signal_type=SignalType.RISK_DETECTED,
                        payload={"module_id": module_id, **item},
                    )
    
    def _generate_module_insights(self, module_id: str, output: Any):
        if output is None:
            return
        
        if isinstance(output, dict):
            if output.get("risk_level") == "CRITICAL":
                self.knowledge_graph.add_insight(GraphInsight(
                    insight_id=f"insight_{module_id}_{datetime.now().strftime('%H%M%S')}",
                    title=f"Critical Risk Detected by {module_id}",
                    description=f"Module {module_id} detected critical risk conditions",
                    severity=InsightSeverity.CRITICAL,
                    source_module=module_id,
                    recommendation="Immediate action required",
                ))
            
            if "health_score" in output:
                score = output["health_score"]
                if isinstance(score, (int, float)) and score < 60:
                    self.knowledge_graph.add_insight(GraphInsight(
                        insight_id=f"insight_health_{module_id}_{datetime.now().strftime('%H%M%S')}",
                        title=f"Low Health Score: {score}/100",
                        description=f"Organizational health score is below threshold",
                        severity=InsightSeverity.WARNING if score >= 40 else InsightSeverity.CRITICAL,
                        source_module=module_id,
                        recommendation="Review governance and risk factors",
                    ))
    
    def get_orchestration_summary(self) -> dict[str, Any]:
        return {
            "registry_summary": self.registry.get_registry_summary(),
            "capability_summary": self.capability_registry.get_registry_summary(),
            "protocol_summary": self.protocol.get_exchange_summary(),
            "graph_summary": self.knowledge_graph.get_graph_summary(),
        }


_orchestrator: Optional[PlatformOrchestrator] = None


def get_orchestrator() -> PlatformOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PlatformOrchestrator()
    return _orchestrator


def initialize_platform(data_path: str = "data/sunrise_care.json"):
    orchestrator = get_orchestrator()
    orchestrator.initialize(data_path)
    return orchestrator


def run_intelligence_pipeline(
    data_path: str = "data/sunrise_care.json",
    execution_mode: ExecutionMode = ExecutionMode.DEPENDENCY_ORDER,
) -> PipelineResult:
    orchestrator = get_orchestrator()
    return orchestrator.run_pipeline(data_path, execution_mode)
