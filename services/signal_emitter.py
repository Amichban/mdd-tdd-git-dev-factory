"""
Signal Emitter Service.
Emits events conforming to Signal Contract.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Optional
from enum import Enum


class SignalType(str, Enum):
    STATUS_CHANGE = "STATUS_CHANGE"
    METRIC_UPDATE = "METRIC_UPDATE"
    ALERT = "ALERT"
    DECISION = "DECISION"
    RESULT = "RESULT"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class System(str, Enum):
    REGISTRY = "REGISTRY"
    ENGINE = "ENGINE"
    OBSERVER = "OBSERVER"


class SignalEmitter:
    """Emit signals conforming to Signal Contract."""

    def __init__(self):
        self._handlers: list = []
        self._history: list[dict] = []
        self._max_history = 1000

    def add_handler(self, handler):
        """Add a signal handler (e.g., WebSocket, Kafka producer)."""
        self._handlers.append(handler)

    def emit(
        self,
        event_type: SignalType,
        system: System,
        component: str,
        node_ref: str,
        payload: dict,
        correlation_id: Optional[str] = None,
    ) -> dict:
        """Emit a signal event."""
        event = {
            'event_id': f"evt_{uuid.uuid4().hex[:12]}",
            'correlation_id': correlation_id or f"run_{uuid.uuid4().hex[:8]}",
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': {
                'system': system.value,
                'component': component,
                'node_ref': node_ref,
            },
            'type': event_type.value,
            'payload': payload,
        }

        # Store in history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Send to handlers
        for handler in self._handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Signal handler error: {e}")

        return event

    def emit_status_change(
        self,
        node_ref: str,
        previous_status: str,
        new_status: str,
        severity: Severity = Severity.MEDIUM,
        summary: str = "",
        correlation_id: Optional[str] = None,
    ) -> dict:
        """Emit a status change event."""
        return self.emit(
            event_type=SignalType.STATUS_CHANGE,
            system=System.ENGINE,
            component="worker",
            node_ref=node_ref,
            payload={
                'previous_status': previous_status,
                'new_status': new_status,
                'severity': severity.value,
                'summary': summary,
            },
            correlation_id=correlation_id,
        )

    def emit_decision(
        self,
        node_ref: str,
        condition: bool,
        reason: str,
        impact: str,
        correlation_id: Optional[str] = None,
    ) -> dict:
        """Emit a decision event."""
        return self.emit(
            event_type=SignalType.DECISION,
            system=System.OBSERVER,
            component="reasoning_core",
            node_ref=node_ref,
            payload={
                'decision': {
                    'condition': condition,
                    'reason': reason,
                    'impact': impact,
                }
            },
            correlation_id=correlation_id,
        )

    def emit_alert(
        self,
        node_ref: str,
        severity: Severity,
        summary: str,
        logs_url: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> dict:
        """Emit an alert event."""
        payload = {
            'severity': severity.value,
            'summary': summary,
        }
        if logs_url:
            payload['logs_url'] = logs_url

        return self.emit(
            event_type=SignalType.ALERT,
            system=System.OBSERVER,
            component="signal_ingestor",
            node_ref=node_ref,
            payload=payload,
            correlation_id=correlation_id,
        )

    def emit_metric(
        self,
        node_ref: str,
        metrics: dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> dict:
        """Emit a metric update event."""
        return self.emit(
            event_type=SignalType.METRIC_UPDATE,
            system=System.ENGINE,
            component="broadcaster",
            node_ref=node_ref,
            payload={'metrics': metrics},
            correlation_id=correlation_id,
        )

    def get_history(self, limit: int = 100) -> list[dict]:
        """Get recent signal history."""
        return self._history[-limit:]

    def get_events_for_node(self, node_ref: str, limit: int = 50) -> list[dict]:
        """Get events for a specific node."""
        events = [
            e for e in self._history
            if e['source']['node_ref'] == node_ref
        ]
        return events[-limit:]


# Singleton instance
_signal_emitter: Optional[SignalEmitter] = None


def get_signal_emitter() -> SignalEmitter:
    """Get the signal emitter singleton."""
    global _signal_emitter
    if _signal_emitter is None:
        _signal_emitter = SignalEmitter()
    return _signal_emitter


# Convenience functions
def emit_status_change(node_ref: str, previous: str, new: str, **kwargs) -> dict:
    """Emit a status change event."""
    return get_signal_emitter().emit_status_change(node_ref, previous, new, **kwargs)


def emit_decision(node_ref: str, condition: bool, reason: str, impact: str, **kwargs) -> dict:
    """Emit a decision event."""
    return get_signal_emitter().emit_decision(node_ref, condition, reason, impact, **kwargs)


def emit_alert(node_ref: str, severity: Severity, summary: str, **kwargs) -> dict:
    """Emit an alert event."""
    return get_signal_emitter().emit_alert(node_ref, severity, summary, **kwargs)
