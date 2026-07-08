from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
from enum import Enum
from collections import defaultdict
import json
import os


class GraphNodeType(Enum):
    ENTITY = "entity"
    MODULE_OUTPUT = "module_output"
    RISK = "risk"
    RECOMMENDATION = "recommendation"
    INSIGHT = "insight"
    SIMULATION = "simulation"
    GOVERNANCE = "governance"
    DEPENDENCY = "dependency"
    PERSON = "person"
    TEAM = "team"
    AGENT = "agent"
    TOOL = "tool"
    WORKFLOW = "workflow"
    POLICY = "policy"


class GraphEdgeType(Enum):
    OWNS = "owns"
    DEPENDS_ON = "depends_on"
    GOVERNS = "governs"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    AFFECTS = "affects"
    REQUIRES = "requires"
    GENERATED_BY = "generated_by"
    RELATED_TO = "related_to"
    CAUSED_BY = "caused_by"
    MITIGATES = "mitigates"
    MONITORS = "monitors"
    REPORTS_TO = "reports_to"
    COLLABORATES_WITH = "collaborates_with"


class InsightSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class GraphNode:
    node_id: str
    node_type: GraphNodeType
    name: str
    properties: dict[str, Any] = field(default_factory=dict)
    source_module: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 1.0


@dataclass
class GraphEdge:
    edge_id: str
    source_id: str
    target_id: str
    edge_type: GraphEdgeType
    properties: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    source_module: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GraphInsight:
    insight_id: str
    title: str
    description: str
    severity: InsightSeverity
    related_nodes: list[str] = field(default_factory=list)
    related_edges: list[str] = field(default_factory=list)
    source_module: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    actionable: bool = True
    recommendation: Optional[str] = None


@dataclass
class GraphPath:
    path_id: str
    nodes: list[str]
    edges: list[str]
    length: int
    path_type: str
    description: str


class UnifiedKnowledgeGraph:
    _instance: Optional[UnifiedKnowledgeGraph] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._adjacency: dict[str, list[str]] = defaultdict(list)
        self._reverse_adjacency: dict[str, list[str]] = defaultdict(list)
        self._node_type_index: dict[GraphNodeType, list[str]] = defaultdict(list)
        self._edge_type_index: dict[GraphEdgeType, list[str]] = defaultdict(list)
        self._insights: list[GraphInsight] = []
        self._source_index: dict[str, list[str]] = defaultdict(list)
        self._created_at = datetime.now().isoformat()
        self._initialized = True
    
    def add_node(self, node: GraphNode) -> GraphNode:
        if node.node_id in self._nodes:
            existing = self._nodes[node.node_id]
            existing.properties.update(node.properties)
            existing.updated_at = datetime.now().isoformat()
            if node.confidence > existing.confidence:
                existing.confidence = node.confidence
            return existing
        
        self._nodes[node.node_id] = node
        self._node_type_index[node.node_type].append(node.node_id)
        
        if node.source_module:
            self._source_index[node.source_module].append(node.node_id)
        
        return node
    
    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        edge_key = f"{edge.source_id}:{edge.edge_type.value}:{edge.target_id}"
        
        if edge_key in self._edges:
            existing = self._edges[edge_key]
            existing.properties.update(edge.properties)
            existing.weight = max(existing.weight, edge.weight)
            return existing
        
        self._edges[edge.edge_id] = edge
        self._adjacency[edge.source_id].append(edge.target_id)
        self._reverse_adjacency[edge.target_id].append(edge.source_id)
        self._edge_type_index[edge.edge_type].append(edge.edge_id)
        
        return edge
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        return self._edges.get(edge_id)
    
    def get_nodes_by_type(self, node_type: GraphNodeType) -> list[GraphNode]:
        node_ids = self._node_type_index.get(node_type, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_edges_by_type(self, edge_type: GraphEdgeType) -> list[GraphEdge]:
        edge_ids = self._edge_type_index.get(edge_type, [])
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]
    
    def get_neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        neighbor_ids = set()
        
        if direction in ("outgoing", "both"):
            neighbor_ids.update(self._adjacency.get(node_id, []))
        
        if direction in ("incoming", "both"):
            neighbor_ids.update(self._reverse_adjacency.get(node_id, []))
        
        return [self._nodes[nid] for nid in neighbor_ids if nid in self._nodes]
    
    def get_edges_for_node(self, node_id: str, direction: str = "both") -> list[GraphEdge]:
        edges = []
        
        if direction in ("outgoing", "both"):
            for target_id in self._adjacency.get(node_id, []):
                edge_key = f"{node_id}:{target_id}"
                for eid, edge in self._edges.items():
                    if edge.source_id == node_id and edge.target_id == target_id:
                        edges.append(edge)
        
        if direction in ("incoming", "both"):
            for source_id in self._reverse_adjacency.get(node_id, []):
                for eid, edge in self._edges.items():
                    if edge.source_id == source_id and edge.target_id == node_id:
                        edges.append(edge)
        
        return edges
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 10) -> Optional[GraphPath]:
        if start_id not in self._nodes or end_id not in self._nodes:
            return None
        
        visited = {start_id}
        queue = [(start_id, [start_id], [])]
        
        while queue:
            current, path, edges = queue.pop(0)
            
            if current == end_id:
                return GraphPath(
                    path_id=f"path_{start_id}_{end_id}",
                    nodes=path,
                    edges=edges,
                    length=len(path) - 1,
                    path_type="shortest",
                    description=f"Path from {self._nodes[start_id].name} to {self._nodes[end_id].name}",
                )
            
            if len(path) > max_depth:
                continue
            
            for target_id in self._adjacency.get(current, []):
                if target_id not in visited:
                    visited.add(target_id)
                    edge_id = None
                    for eid, edge in self._edges.items():
                        if edge.source_id == current and edge.target_id == target_id:
                            edge_id = eid
                            break
                    queue.append((target_id, path + [target_id], edges + [edge_id]))
        
        return None
    
    def find_all_paths(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5,
    ) -> list[GraphPath]:
        if start_id not in self._nodes or end_id not in self._nodes:
            return []
        
        paths = []
        self._dfs_paths(start_id, end_id, set(), [start_id], [], paths, max_depth)
        return paths
    
    def _dfs_paths(
        self,
        current: str,
        end: str,
        visited: set,
        path: list,
        edges: list,
        all_paths: list,
        max_depth: int,
    ):
        if len(path) > max_depth:
            return
        
        if current == end and len(path) > 1:
            all_paths.append(GraphPath(
                path_id=f"path_{path[0]}_{path[-1]}_{len(all_paths)}",
                nodes=list(path),
                edges=list(edges),
                length=len(path) - 1,
                path_type="alternative",
                description=f"Alternative path",
            ))
            return
        
        visited.add(current)
        
        for target_id in self._adjacency.get(current, []):
            if target_id not in visited:
                edge_id = None
                for eid, edge in self._edges.items():
                    if edge.source_id == current and edge.target_id == target_id:
                        edge_id = eid
                        break
                self._dfs_paths(target_id, end, visited, path + [target_id], edges + [edge_id], all_paths, max_depth)
        
        visited.remove(current)
    
    def get_subgraph(self, node_ids: list[str], include_edges: bool = True) -> dict[str, Any]:
        sub_nodes = {nid: self._nodes[nid] for nid in node_ids if nid in self._nodes}
        
        sub_edges = {}
        if include_edges:
            for edge in self._edges.values():
                if edge.source_id in sub_nodes and edge.target_id in sub_nodes:
                    sub_edges[edge.edge_id] = edge
        
        return {
            "nodes": {nid: n.__dict__ for nid, n in sub_nodes.items()},
            "edges": {eid: e.__dict__ for eid, e in sub_edges.items()},
        }
    
    def add_insight(self, insight: GraphInsight) -> GraphInsight:
        self._insights.append(insight)
        return insight
    
    def get_insights(
        self,
        severity: Optional[InsightSeverity] = None,
        source_module: Optional[str] = None,
    ) -> list[GraphInsight]:
        filtered = self._insights
        
        if severity:
            filtered = [i for i in filtered if i.severity == severity]
        if source_module:
            filtered = [i for i in filtered if i.source_module == source_module]
        
        return filtered
    
    def get_centrality_scores(self) -> dict[str, float]:
        scores = {}
        n = len(self._nodes)
        
        if n == 0:
            return scores
        
        for node_id in self._nodes:
            in_degree = len(self._reverse_adjacency.get(node_id, []))
            out_degree = len(self._adjacency.get(node_id, []))
            total_degree = in_degree + out_degree
            scores[node_id] = total_degree / (n - 1) if n > 1 else 0
        
        return scores
    
    def get_graph_summary(self) -> dict[str, Any]:
        node_type_counts = {}
        for node_type in GraphNodeType:
            count = len(self._node_type_index.get(node_type, []))
            if count > 0:
                node_type_counts[node_type.value] = count
        
        edge_type_counts = {}
        for edge_type in GraphEdgeType:
            count = len(self._edge_type_index.get(edge_type, []))
            if count > 0:
                edge_type_counts[edge_type.value] = count
        
        centrality = self.get_centrality_scores()
        top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "node_type_counts": node_type_counts,
            "edge_type_counts": edge_type_counts,
            "insights_count": len(self._insights),
            "top_central_nodes": [
                {"node_id": nid, "score": score, "name": self._nodes[nid].name if nid in self._nodes else "unknown"}
                for nid, score in top_central
            ],
            "created_at": self._created_at,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.get_graph_summary(), indent=2, default=str)
    
    def save(self, path: str = "data/knowledge_graph.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        data = {
            "summary": self.get_graph_summary(),
            "nodes": {nid: n.__dict__ for nid, n in self._nodes.items()},
            "edges": {eid: e.__dict__ for eid, e in self._edges.items()},
            "insights": [i.__dict__ for i in self._insights],
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)


_graph: Optional[UnifiedKnowledgeGraph] = None


def get_knowledge_graph() -> UnifiedKnowledgeGraph:
    global _graph
    if _graph is None:
        _graph = UnifiedKnowledgeGraph()
    return _graph


def add_entity_to_graph(
    entity_id: str,
    name: str,
    node_type: GraphNodeType,
    properties: Optional[dict] = None,
    source_module: Optional[str] = None,
) -> GraphNode:
    graph = get_knowledge_graph()
    node = GraphNode(
        node_id=entity_id,
        node_type=node_type,
        name=name,
        properties=properties or {},
        source_module=source_module,
    )
    return graph.add_node(node)


def add_relationship_to_graph(
    source_id: str,
    target_id: str,
    edge_type: GraphEdgeType,
    properties: Optional[dict] = None,
    weight: float = 1.0,
    source_module: Optional[str] = None,
) -> GraphEdge:
    graph = get_knowledge_graph()
    edge = GraphEdge(
        edge_id=f"{source_id}_{edge_type.value}_{target_id}",
        source_id=source_id,
        target_id=target_id,
        edge_type=edge_type,
        properties=properties or {},
        weight=weight,
        source_module=source_module,
    )
    return graph.add_edge(edge)
