"""
Event Emitter for Algorithm Observability

Provides simple functions for algorithms to emit decision and result events
to the existing Observer event bus. This enables full explainability without
adding new infrastructure.

Usage:
    from services.events import emit, decision, result

    def my_algorithm(inputs, correlation_id):
        # Emit a decision point
        is_valid = decision(
            correlation_id=correlation_id,
            node_id="algo.my_algorithm",
            step="validate_input",
            condition=inputs.value > 0,
            reason=f"Input value is {inputs.value}",
            impact="Proceed with calculation" if inputs.value > 0 else "Skip calculation"
        )

        # Emit final result
        return result(
            correlation_id=correlation_id,
            node_id="algo.my_algorithm",
            value=calculated_result,
            summary="Calculated X based on Y",
            formula="X = Y * 2"
        )
"""

from datetime import datetime, timezone
from typing import Any
import json
import logging

# Configure logging - in production this would go to the event bus
logger = logging.getLogger("events")


def emit(event: dict) -> None:
    """
    Emit an event to the Observer bus.

    In production, this would publish to Kafka/Redis/etc.
    For now, it logs the event in structured format.
    """
    # Ensure timestamp
    if "timestamp" not in event:
        event["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Log for development
    logger.info(f"EVENT: {json.dumps(event)}")

    # TODO: In production, publish to event bus
    # bus.publish(event)


def decision(
    correlation_id: str,
    node_id: str,
    step: str,
    condition: bool,
    reason: str,
    impact: str
) -> bool:
    """
    Emit a decision_evaluated event and return the condition result.

    This allows inline usage:
        if decision(..., condition=x > 0, ...):
            # do something

    Args:
        correlation_id: Links to parent job run
        node_id: Algorithm identifier (e.g., "algo.tax_calculator")
        step: Decision point ID (e.g., "check_state")
        condition: The boolean result of the evaluation
        reason: Human-readable explanation of what was evaluated
        impact: What this decision means for the outcome

    Returns:
        The condition value (passthrough for inline usage)
    """
    emit({
        "event_type": "decision_evaluated",
        "correlation_id": correlation_id,
        "node_id": node_id,
        "step": step,
        "condition": condition,
        "reason": reason,
        "impact": impact
    })

    return condition


def result(
    correlation_id: str,
    node_id: str,
    value: Any,
    summary: str,
    formula: str | None = None
) -> Any:
    """
    Emit a result_computed event and return the value.

    This allows inline usage:
        return result(..., value=calculated, ...)

    Args:
        correlation_id: Links to parent job run
        node_id: Algorithm identifier
        value: The computed result
        summary: Human-readable summary of what was computed
        formula: Optional formula/calculation used

    Returns:
        The value (passthrough for inline usage)
    """
    event = {
        "event_type": "result_computed",
        "correlation_id": correlation_id,
        "node_id": node_id,
        "result": value,
        "summary": summary
    }

    if formula:
        event["formula"] = formula

    emit(event)

    return value


def job_started(correlation_id: str, node_id: str, inputs: dict | None = None) -> None:
    """Emit job_started event."""
    event = {
        "event_type": "job_started",
        "correlation_id": correlation_id,
        "node_id": node_id
    }
    if inputs:
        event["inputs"] = inputs
    emit(event)


def job_completed(correlation_id: str, node_id: str, duration_ms: int | None = None) -> None:
    """Emit job_completed event."""
    event = {
        "event_type": "job_completed",
        "correlation_id": correlation_id,
        "node_id": node_id,
        "status": "completed"
    }
    if duration_ms:
        event["duration_ms"] = duration_ms
    emit(event)


def job_failed(correlation_id: str, node_id: str, error: str) -> None:
    """Emit job_failed event."""
    emit({
        "event_type": "job_failed",
        "correlation_id": correlation_id,
        "node_id": node_id,
        "status": "failed",
        "error": error
    })
