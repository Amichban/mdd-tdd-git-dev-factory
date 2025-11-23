"""
Events API endpoints.
GET /api/node/:id/history - Fetch past events.
WebSocket /ws/events - Stream live signals.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import asyncio
import json

from services.signal_emitter import get_signal_emitter

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/history")
async def get_event_history(limit: int = Query(100, ge=1, le=1000)):
    """Get recent event history."""
    emitter = get_signal_emitter()
    return emitter.get_history(limit)


@router.get("/node/{node_id}")
async def get_node_events(
    node_id: str,
    limit: int = Query(50, ge=1, le=500)
):
    """Get events for a specific node."""
    emitter = get_signal_emitter()
    return emitter.get_events_for_node(node_id, limit)


# WebSocket connections for live streaming
active_connections: list[WebSocket] = []


@router.websocket("/ws")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint for streaming live events."""
    await websocket.accept()
    active_connections.append(websocket)

    # Register as signal handler
    emitter = get_signal_emitter()

    async def send_to_ws(event: dict):
        try:
            await websocket.send_json(event)
        except:
            pass

    def sync_handler(event: dict):
        asyncio.create_task(send_to_ws(event))

    emitter.add_handler(sync_handler)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to event stream"
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()

            # Handle subscription requests
            try:
                msg = json.loads(data)
                if msg.get("type") == "subscribe":
                    await websocket.send_json({
                        "type": "subscribed",
                        "filter": msg.get("filter", {})
                    })
                elif msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast_event(event: dict):
    """Broadcast event to all connected WebSocket clients."""
    for connection in active_connections:
        try:
            await connection.send_json(event)
        except:
            active_connections.remove(connection)
