from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
from enum import Enum
import json


class CapabilityType(Enum):
    INPUT = "input"
    OUTPUT = "output"
    PROCESS = "process"
    QUERY = "query"
    TRANSFORM = "transform"


class DataType(Enum):
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    RISK = "risk"
    RECOMMENDATION = "recommendation"
    SIMULATION = "simulation"
    GOVERNANCE = "governance"
    ACCOUNTABILITY = "accountability"
    CONTEXT = "context"
    KNOWLEDGE = "knowledge"
    METRICS = "metrics"
    GRAPH = "graph"
    VOICE = "voice"
    BRIEFING = "briefing"


@dataclass
class DataDescriptor:
    data_type: DataType
    format: str
    schema: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class CapabilityDefinition:
    capability_id: str
    name: str
    capability_type: CapabilityType
    description: str
    input_descriptors: list[DataDescriptor] = field(default_factory=list)
    output_descriptors: list[DataDescriptor] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    examples: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class CapabilityRegistration:
    module_id: str
    capability: CapabilityDefinition
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    last_used: Optional[str] = None


class CapabilityRegistry:
    _instance: Optional[CapabilityRegistry] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._capabilities: dict[str, CapabilityRegistration] = {}
        self._module_index: dict[str, list[str]] = {}
        self._type_index: dict[CapabilityType, list[str]] = {}
        self._data_type_index: dict[DataType, list[str]] = {}
        self._initialized = True
    
    def register_capability(
        self,
        module_id: str,
        capability: CapabilityDefinition,
    ) -> CapabilityRegistration:
        if capability.capability_id in self._capabilities:
            raise ValueError(f"Capability {capability.capability_id} already registered")
        
        registration = CapabilityRegistration(
            module_id=module_id,
            capability=capability,
        )
        
        self._capabilities[capability.capability_id] = registration
        
        if module_id not in self._module_index:
            self._module_index[module_id] = []
        self._module_index[module_id].append(capability.capability_id)
        
        if capability.capability_type not in self._type_index:
            self._type_index[capability.capability_type] = []
        self._type_index[capability.capability_type].append(capability.capability_id)
        
        for desc in capability.output_descriptors:
            if desc.data_type not in self._data_type_index:
                self._data_type_index[desc.data_type] = []
            self._data_type_index[desc.data_type].append(capability.capability_id)
        
        return registration
    
    def get_capability(self, capability_id: str) -> Optional[CapabilityRegistration]:
        return self._capabilities.get(capability_id)
    
    def get_capabilities_for_module(self, module_id: str) -> list[CapabilityRegistration]:
        cap_ids = self._module_index.get(module_id, [])
        return [self._capabilities[cid] for cid in cap_ids if cid in self._capabilities]
    
    def get_capabilities_by_type(self, cap_type: CapabilityType) -> list[CapabilityRegistration]:
        cap_ids = self._type_index.get(cap_type, [])
        return [self._capabilities[cid] for cid in cap_ids if cid in self._capabilities]
    
    def get_producers_of(self, data_type: DataType) -> list[CapabilityRegistration]:
        cap_ids = self._data_type_index.get(data_type, [])
        return [
            self._capabilities[cid]
            for cid in cap_ids
            if cid in self._capabilities
            and self._capabilities[cid].capability.capability_type in (CapabilityType.OUTPUT, CapabilityType.TRANSFORM)
        ]
    
    def get_consumers_of(self, data_type: DataType) -> list[CapabilityRegistration]:
        result = []
        for reg in self._capabilities.values():
            for desc in reg.capability.input_descriptors:
                if desc.data_type == data_type:
                    result.append(reg)
                    break
        return result
    
    def find_compatible_capabilities(
        self,
        producer_data_type: DataType,
        consumer_module_id: Optional[str] = None,
    ) -> list[tuple[CapabilityRegistration, CapabilityRegistration]]:
        producers = self.get_producers_of(producer_data_type)
        consumers = self.get_consumers_of(producer_data_type)
        
        pairs = []
        for producer in producers:
            for consumer in consumers:
                if consumer_module_id and consumer.module_id != consumer_module_id:
                    continue
                if producer.module_id != consumer.module_id:
                    pairs.append((producer, consumer))
        
        return pairs
    
    def mark_used(self, capability_id: str):
        if capability_id in self._capabilities:
            self._capabilities[capability_id].usage_count += 1
            self._capabilities[capability_id].last_used = datetime.now().isoformat()
    
    def get_registry_summary(self) -> dict[str, Any]:
        type_counts = {}
        for cap_type in CapabilityType:
            type_counts[cap_type.value] = len(self._type_index.get(cap_type, []))
        
        data_type_counts = {}
        for dt in DataType:
            data_type_counts[dt.value] = len(self._data_type_index.get(dt, []))
        
        return {
            "total_capabilities": len(self._capabilities),
            "type_counts": type_counts,
            "data_type_counts": data_type_counts,
            "module_coverage": {
                module_id: len(cap_ids)
                for module_id, cap_ids in self._module_index.items()
            },
            "capabilities": [
                {
                    "capability_id": reg.capability.capability_id,
                    "module_id": reg.module_id,
                    "name": reg.capability.name,
                    "type": reg.capability.capability_type.value,
                    "usage_count": reg.usage_count,
                }
                for reg in self._capabilities.values()
            ],
        }


_registry: Optional[CapabilityRegistry] = None


def get_capability_registry() -> CapabilityRegistry:
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
    return _registry


def register_capability(
    module_id: str,
    capability_id: str,
    name: str,
    capability_type: CapabilityType,
    description: str,
    input_descriptors: Optional[list[DataDescriptor]] = None,
    output_descriptors: Optional[list[DataDescriptor]] = None,
    parameters: Optional[dict] = None,
) -> CapabilityRegistration:
    registry = get_capability_registry()
    
    capability = CapabilityDefinition(
        capability_id=capability_id,
        name=name,
        capability_type=capability_type,
        description=description,
        input_descriptors=input_descriptors or [],
        output_descriptors=output_descriptors or [],
        parameters=parameters or {},
    )
    
    return registry.register_capability(module_id, capability)
