from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from datetime import datetime
from enum import Enum
import json
import uuid
from collections import defaultdict


class MessageType(Enum):
    SIGNAL = "signal"
    QUERY = "query"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"
    BROADCAST = "broadcast"


class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class SignalType(Enum):
    RISK_DETECTED = "risk_detected"
    RISK_CHANGED = "risk_changed"
    DEPENDENCY_FOUND = "dependency_found"
    DEPENDENCY_BROKEN = "dependency_broken"
    ENTITY_CREATED = "entity_created"
    ENTITY_UPDATED = "entity_updated"
    ENTITY_REMOVED = "entity_removed"
    GOVERNANCE_GAP = "governance_gap"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    SIMULATION_COMPLETED = "simulation_completed"
    HEALTH_SCORE_CHANGED = "health_score_changed"
    ORPHAN_DETECTED = "orphan_detected"
    SPOF_DETECTED = "spof_detected"
    CASCADE_RISK = "cascade_risk"
    KNOWLEDGE_GAP = "knowledge_gap"


@dataclass
class IntelligenceMessage:
    message_id: str
    message_type: MessageType
    source_module: str
    target_module: Optional[str]
    timestamp: str
    payload: dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    signal_type: Optional[SignalType] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl_seconds: Optional[int] = None


@dataclass
class MessageHandler:
    handler_id: str
    module_id: str
    message_type: MessageType
    callback: Callable[[IntelligenceMessage], Optional[dict]]
    filter_signal_type: Optional[SignalType] = None


@dataclass
class MessageLog:
    message: IntelligenceMessage
    handled_by: list[str] = field(default_factory=list)
    responses: list[dict] = field(default_factory=list)
    logged_at: str = field(default_factory=lambda: datetime.now().isoformat())


class IntelligenceExchangeProtocol:
    _instance: Optional[IntelligenceExchangeProtocol] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._handlers: dict[MessageType, list[MessageHandler]] = defaultdict(list)
        self._signal_handlers: dict[SignalType, list[MessageHandler]] = defaultdict(list)
        self._message_log: list[MessageLog] = []
        self._pending_queries: dict[str, IntelligenceMessage] = {}
        self._subscribers: dict[str, list[str]] = defaultdict(list)
        self._initialized = True
    
    def register_handler(
        self,
        module_id: str,
        message_type: MessageType,
        callback: Callable[[IntelligenceMessage], Optional[dict]],
        filter_signal_type: Optional[SignalType] = None,
    ) -> MessageHandler:
        handler_id = f"{module_id}_{message_type.value}_{uuid.uuid4().hex[:8]}"
        
        handler = MessageHandler(
            handler_id=handler_id,
            module_id=module_id,
            message_type=message_type,
            callback=callback,
            filter_signal_type=filter_signal_type,
        )
        
        self._handlers[message_type].append(handler)
        
        if filter_signal_type:
            self._signal_handlers[filter_signal_type].append(handler)
        
        return handler
    
    def unregister_handler(self, handler_id: str):
        for message_type in self._handlers:
            self._handlers[message_type] = [
                h for h in self._handlers[message_type] if h.handler_id != handler_id
            ]
        
        for signal_type in self._signal_handlers:
            self._signal_handlers[signal_type] = [
                h for h in self._signal_handlers[signal_type] if h.handler_id != handler_id
            ]
    
    def subscribe(self, module_id: str, signal_type: SignalType):
        self._subscribers[signal_type.value].append(module_id)
    
    def unsubscribe(self, module_id: str, signal_type: SignalType):
        if signal_type.value in self._subscribers:
            self._subscribers[signal_type.value] = [
                m for m in self._subscribers[signal_type.value] if m != module_id
            ]
    
    def emit_signal(
        self,
        source_module: str,
        signal_type: SignalType,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> IntelligenceMessage:
        message = IntelligenceMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.SIGNAL,
            source_module=source_module,
            target_module=None,
            timestamp=datetime.now().isoformat(),
            payload=payload,
            priority=priority,
            signal_type=signal_type,
        )
        
        self._dispatch_message(message)
        return message
    
    def send_query(
        self,
        source_module: str,
        target_module: str,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> IntelligenceMessage:
        message = IntelligenceMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.QUERY,
            source_module=source_module,
            target_module=target_module,
            timestamp=datetime.now().isoformat(),
            payload=payload,
            priority=priority,
        )
        
        self._pending_queries[message.message_id] = message
        self._dispatch_message(message)
        return message
    
    def send_response(
        self,
        source_module: str,
        reply_to: str,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> IntelligenceMessage:
        message = IntelligenceMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.RESPONSE,
            source_module=source_module,
            target_module=None,
            timestamp=datetime.now().isoformat(),
            payload=payload,
            priority=priority,
            reply_to=reply_to,
        )
        
        if reply_to in self._pending_queries:
            del self._pending_queries[reply_to]
        
        self._dispatch_message(message)
        return message
    
    def broadcast_event(
        self,
        source_module: str,
        event_type: str,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> IntelligenceMessage:
        message = IntelligenceMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.BROADCAST,
            source_module=source_module,
            target_module=None,
            timestamp=datetime.now().isoformat(),
            payload={**payload, "event_type": event_type},
            priority=priority,
        )
        
        self._dispatch_message(message)
        return message
    
    def send_command(
        self,
        source_module: str,
        target_module: str,
        command: str,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.HIGH,
    ) -> IntelligenceMessage:
        message = IntelligenceMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.COMMAND,
            source_module=source_module,
            target_module=target_module,
            timestamp=datetime.now().isoformat(),
            payload={**payload, "command": command},
            priority=priority,
        )
        
        self._dispatch_message(message)
        return message
    
    def _dispatch_message(self, message: IntelligenceMessage):
        log = MessageLog(message=message)
        
        handlers = self._handlers.get(message.message_type, [])
        
        if message.signal_type and message.signal_type in self._signal_handlers:
            handlers = handlers + self._signal_handlers[message.signal_type]
        
        if message.target_module:
            handlers = [h for h in handlers if h.module_id == message.target_module]
        
        for handler in handlers:
            if handler.filter_signal_type and handler.filter_signal_type != message.signal_type:
                continue
            
            try:
                response = handler.callback(message)
                log.handled_by.append(handler.handler_id)
                if response:
                    log.responses.append(response)
            except Exception as e:
                log.responses.append({
                    "error": str(e),
                    "handler_id": handler.handler_id,
                })
        
        self._message_log.append(log)
    
    def get_pending_queries(self) -> list[IntelligenceMessage]:
        return list(self._pending_queries.values())
    
    def get_message_log(
        self,
        message_type: Optional[MessageType] = None,
        source_module: Optional[str] = None,
        signal_type: Optional[SignalType] = None,
        limit: int = 100,
    ) -> list[MessageLog]:
        filtered = self._message_log
        
        if message_type:
            filtered = [l for l in filtered if l.message.message_type == message_type]
        if source_module:
            filtered = [l for l in filtered if l.message.source_module == source_module]
        if signal_type:
            filtered = [l for l in filtered if l.message.signal_type == signal_type]
        
        return filtered[-limit:]
    
    def get_exchange_summary(self) -> dict[str, Any]:
        type_counts = {}
        for log in self._message_log:
            msg_type = log.message.message_type.value
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        signal_counts = {}
        for log in self._message_log:
            if log.message.signal_type:
                sig_type = log.message.signal_type.value
                signal_counts[sig_type] = signal_counts.get(sig_type, 0) + 1
        
        source_counts = {}
        for log in self._message_log:
            source = log.message.source_module
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            "total_messages": len(self._message_log),
            "pending_queries": len(self._pending_queries),
            "message_type_counts": type_counts,
            "signal_type_counts": signal_counts,
            "source_module_counts": source_counts,
            "handler_count": sum(len(handlers) for handlers in self._handlers.values()),
            "subscriber_count": sum(len(subs) for subs in self._subscribers.values()),
        }


_protocol: Optional[IntelligenceExchangeProtocol] = None


def get_protocol() -> IntelligenceExchangeProtocol:
    global _protocol
    if _protocol is None:
        _protocol = IntelligenceExchangeProtocol()
    return _protocol


def emit_signal(
    source_module: str,
    signal_type: SignalType,
    payload: dict[str, Any],
    priority: MessagePriority = MessagePriority.NORMAL,
) -> IntelligenceMessage:
    return get_protocol().emit_signal(source_module, signal_type, payload, priority)


def send_query(
    source_module: str,
    target_module: str,
    payload: dict[str, Any],
) -> IntelligenceMessage:
    return get_protocol().send_query(source_module, target_module, payload)


def send_response(
    source_module: str,
    reply_to: str,
    payload: dict[str, Any],
) -> IntelligenceMessage:
    return get_protocol().send_response(source_module, reply_to, payload)
