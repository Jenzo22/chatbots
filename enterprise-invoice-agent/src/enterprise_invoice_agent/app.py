"""FastAPI app: run workflow, HITL resume, state inspection. All responses PII-redacted."""

from typing import Any

from fastapi import FastAPI, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field

from .graph import build_graph
from .persistence import get_checkpointer
from .security import redact_pii
from .state import InvoiceReconciliationState

app = FastAPI(title="Enterprise Invoice Reconciliation Agent", version="0.1.0")

# Lazy graph: build once with SQLite checkpointer
_checkpointer = None


def get_graph():
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = get_checkpointer()
    return build_graph(_checkpointer)


class RunRequest(BaseModel):
    """Start a new reconciliation run."""

    thread_id: str = Field(description="Thread ID for state persistence")
    vendor_id: str | None = Field(default=None, description="Optional vendor filter")


class ResumeRequest(BaseModel):
    """Resume after HITL interrupt (approve/reject)."""

    thread_id: str = Field(description="Same thread_id as the run that was interrupted")
    approved: bool = Field(description="True to approve payment, False to reject")


@app.post("/run")
def run(req: RunRequest) -> dict[str, Any]:
    """Start reconciliation. Returns state or __interrupt__ when waiting for approval."""
    graph = get_graph()
    config = {"configurable": {"thread_id": req.thread_id}}
    initial: InvoiceReconciliationState = {
        "vendor_id": req.vendor_id,
        "messages": [],
        "retry_count": 0,
    }
    result = graph.invoke(initial, config=config)
    return redact_pii(_state_to_response(result))


@app.post("/resume")
def resume(req: ResumeRequest) -> dict[str, Any]:
    """Resume after human approval. Call with approved=True/False after /run returns __interrupt__."""
    graph = get_graph()
    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke(Command(resume=req.approved), config=config)
    return redact_pii(_state_to_response(result))


@app.get("/state")
def get_state(thread_id: str) -> dict[str, Any]:
    """Get current state for a thread (e.g. for HITL UI). PII redacted."""
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread not found")
    return redact_pii(_state_to_response(dict(snapshot.values)))


def _state_to_response(state: dict) -> dict:
    """Normalize state for JSON; include __interrupt__ if present (from invoke)."""
    out = {k: v for k, v in state.items() if v is not None}
    return out