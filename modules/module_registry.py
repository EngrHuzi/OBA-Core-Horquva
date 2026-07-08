from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime
from enum import Enum
import json
import os


class ModuleStatus(Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


class ModulePhase(Enum):
    CORE_INTELLIGENCE = "phase_1"
    PLATFORM_FOUNDATION = "phase_2"
    GOVERNANCE_ACCOUNTABILITY = "phase_3"
    EXECUTIVE_VOICE = "phase_4"
    ORGANIZATIONAL_SCALE = "phase_5"
    ARCHITECTURE = "architecture"


@dataclass
class ModuleCapability:
    name: str
    description: str
    input_types: list[str]
    output_types: list[str]
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModuleDependency:
    module_id: str
    dependency_type: str  # "requires" | "optional" | "enhances"
    description: str


@dataclass
class ModuleMetadata:
    module_id: str
    name: str
    version: str
    phase: ModulePhase
    description: str
    author: str
    capabilities: list[ModuleCapability] = field(default_factory=list)
    dependencies: list[ModuleDependency] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class ModuleState:
    status: ModuleStatus
    last_executed: Optional[str] = None
    execution_count: int = 0
    last_error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    output_hash: Optional[str] = None


@dataclass
class ModuleRegistration:
    metadata: ModuleMetadata
    state: ModuleState
    run_function: Optional[Callable] = None
    display_function: Optional[Callable] = None


class ModuleRegistry:
    _instance: Optional[ModuleRegistry] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._modules: dict[str, ModuleRegistration] = {}
        self._phase_index: dict[ModulePhase, list[str]] = {p: [] for p in ModulePhase}
        self._tag_index: dict[str, list[str]] = {}
        self._created_at = datetime.now().isoformat()
        self._initialized = True
    
    def register(
        self,
        metadata: ModuleMetadata,
        run_function: Optional[Callable] = None,
        display_function: Optional[Callable] = None,
    ) -> ModuleRegistration:
        if metadata.module_id in self._modules:
            raise ValueError(f"Module {metadata.module_id} already registered")
        
        state = ModuleState(status=ModuleStatus.REGISTERED)
        registration = ModuleRegistration(
            metadata=metadata,
            state=state,
            run_function=run_function,
            display_function=display_function,
        )
        
        self._modules[metadata.module_id] = registration
        self._phase_index[metadata.phase].append(metadata.module_id)
        
        for tag in metadata.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(metadata.module_id)
        
        return registration
    
    def get(self, module_id: str) -> Optional[ModuleRegistration]:
        return self._modules.get(module_id)
    
    def get_by_phase(self, phase: ModulePhase) -> list[ModuleRegistration]:
        module_ids = self._phase_index.get(phase, [])
        return [self._modules[mid] for mid in module_ids if mid in self._modules]
    
    def get_by_tag(self, tag: str) -> list[ModuleRegistration]:
        module_ids = self._tag_index.get(tag, [])
        return [self._modules[mid] for mid in module_ids if mid in self._modules]
    
    def get_all(self) -> list[ModuleRegistration]:
        return list(self._modules.values())
    
    def get_dependency_order(self) -> list[str]:
        visited = set()
        order = []
        
        def dfs(module_id: str):
            if module_id in visited:
                return
            visited.add(module_id)
            reg = self._modules.get(module_id)
            if reg:
                for dep in reg.metadata.dependencies:
                    if dep.dependency_type == "requires":
                        dfs(dep.module_id)
            order.append(module_id)
        
        for module_id in self._modules:
            dfs(module_id)
        
        return order
    
    def update_status(self, module_id: str, status: ModuleStatus):
        if module_id in self._modules:
            self._modules[module_id].state.status = status
            if status == ModuleStatus.COMPLETED:
                self._modules[module_id].state.last_executed = datetime.now().isoformat()
                self._modules[module_id].state.execution_count += 1
    
    def update_execution_time(self, module_id: str, time_ms: float):
        if module_id in self._modules:
            self._modules[module_id].state.execution_time_ms = time_ms
    
    def update_error(self, module_id: str, error: str):
        if module_id in self._modules:
            self._modules[module_id].state.last_error = error
            self._modules[module_id].state.status = ModuleStatus.FAILED
    
    def get_registry_summary(self) -> dict[str, Any]:
        phase_counts = {}
        for phase in ModulePhase:
            phase_counts[phase.value] = len(self._phase_index.get(phase, []))
        
        status_counts = {}
        for reg in self._modules.values():
            status = reg.state.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_modules": len(self._modules),
            "created_at": self._created_at,
            "phase_counts": phase_counts,
            "status_counts": status_counts,
            "modules": [
                {
                    "module_id": reg.metadata.module_id,
                    "name": reg.metadata.name,
                    "phase": reg.metadata.phase.value,
                    "status": reg.state.status.value,
                    "execution_count": reg.state.execution_count,
                }
                for reg in self._modules.values()
            ],
        }
    
    def to_json(self) -> str:
        return json.dumps(self.get_registry_summary(), indent=2, default=str)
    
    def save(self, path: str = "data/module_registry.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_registry_summary(), f, indent=2, default=str)


_registry: Optional[ModuleRegistry] = None


def get_registry() -> ModuleRegistry:
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
    return _registry


def register_module(
    module_id: str,
    name: str,
    phase: ModulePhase,
    description: str,
    author: str = "Horquva",
    version: str = "1.0.0",
    capabilities: Optional[list[ModuleCapability]] = None,
    dependencies: Optional[list[ModuleDependency]] = None,
    input_schema: Optional[dict] = None,
    output_schema: Optional[dict] = None,
    tags: Optional[list[str]] = None,
    run_function: Optional[Callable] = None,
    display_function: Optional[Callable] = None,
) -> ModuleRegistration:
    registry = get_registry()
    
    metadata = ModuleMetadata(
        module_id=module_id,
        name=name,
        version=version,
        phase=phase,
        description=description,
        author=author,
        capabilities=capabilities or [],
        dependencies=dependencies or [],
        input_schema=input_schema or {},
        output_schema=output_schema or {},
        tags=tags or [],
    )
    
    return registry.register(metadata, run_function, display_function)
