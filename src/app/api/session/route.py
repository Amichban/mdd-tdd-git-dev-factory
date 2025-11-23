"""
Session API endpoints.
POST /api/session - Start a headless Claude session.
POST /api/session/:id/prompt - Send message to session.
"""

import uuid
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/session", tags=["Session"])

# In-memory session store (use Redis in production)
sessions: dict = {}


class SessionCreate(BaseModel):
    """Request to create a new session."""
    context: Optional[str] = None
    allowed_tools: list[str] = ["Read", "Glob", "Grep"]
    system_prompt: Optional[str] = None


class SessionPrompt(BaseModel):
    """Request to send a prompt to a session."""
    message: str


class Session(BaseModel):
    """Session response model."""
    id: str
    status: str
    context: Optional[str]
    messages: list[dict]


@router.post("/", response_model=Session, status_code=201)
async def create_session(data: SessionCreate):
    """Create a new headless Claude session."""
    session_id = str(uuid.uuid4())

    session = {
        "id": session_id,
        "status": "active",
        "context": data.context,
        "allowed_tools": data.allowed_tools,
        "system_prompt": data.system_prompt,
        "messages": [],
    }

    sessions[session_id] = session

    return Session(
        id=session_id,
        status="active",
        context=data.context,
        messages=[]
    )


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get session details."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    return Session(
        id=session["id"],
        status=session["status"],
        context=session["context"],
        messages=session["messages"]
    )


@router.post("/{session_id}/prompt")
async def send_prompt(session_id: str, data: SessionPrompt):
    """Send a prompt to the session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]

    # Add user message
    session["messages"].append({
        "role": "user",
        "content": data.message
    })

    # Build claude command
    allowed_tools = ",".join(session["allowed_tools"])
    cmd = [
        "claude",
        "-p", data.message,
        "--allowedTools", allowed_tools,
        "--output-format", "json"
    ]

    try:
        # Run claude in headless mode
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        response = result.stdout or result.stderr

        # Add assistant message
        session["messages"].append({
            "role": "assistant",
            "content": response
        })

        return {
            "session_id": session_id,
            "response": response,
            "exit_code": result.returncode
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Claude request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """End a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[session_id]["status"] = "closed"
    del sessions[session_id]
    return None
