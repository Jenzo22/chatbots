"""LangGraph: Manager workflow with HITL and self-correction."""

from decimal import Decimal

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from .config import HITL_APPROVAL_THRESHOLD_USD
from .state import InvoiceReconciliationState
from .worker import get_payment_summary, reconcile_step
from .tools import execute_payment


def reconcile_node(state: InvoiceReconciliationState) -> dict:
    """
    Worker step: fetch invoices and match to POs.
    Self-correction: retry and fallback happen inside reconcile_step.
    """
    vendor_id = state.get("vendor_id")
    retry_count = state.get("retry_count") or 0
    reconciled, err, used_fallback = reconcile_step(vendor_id=vendor_id, limit=5)
    updates: InvoiceReconciliationState = {
        "reconciled": reconciled,
        "used_fallback": used_fallback,
        "retry_count": retry_count + (1 if err else 0),
        "last_error": str(err) if err else None,
    }
    if err and used_fallback and not reconciled:
        updates["status"] = "failed"
    elif reconciled:
        # Pick first reconciled item for payment for demo
        first = reconciled[0] if reconciled else {}
        inv = first.get("invoice") or {}
        amount = inv.get("amount")
        if amount is not None:
            updates["pending_payment"] = {
                "invoice_id": inv.get("invoice_id", ""),
                "amount": float(amount) if not isinstance(amount, (int, float)) else amount,
                "vendor_id": inv.get("vendor_id", ""),
            }
    return updates


def check_approval_node(state: InvoiceReconciliationState):
    """
    Human-in-the-loop: if payment amount >= threshold, interrupt and wait for approval.
    Do NOT wrap interrupt() in try/except.
    """
    pending = state.get("pending_payment") or {}
    amount_usd = pending.get("amount") or 0
    invoice_id = pending.get("invoice_id", "")
    threshold = HITL_APPROVAL_THRESHOLD_USD
    needs_approval = amount_usd >= threshold

    if not needs_approval:
        return {"approval": True, "status": "pending", "hitl_prompt": None}

    get_payment_summary(invoice_id, Decimal(str(amount_usd)))  # optional: use for audit
    prompt = {
        "question": f"Ready to pay this ${amount_usd:,.2f} invoice. Approve?",
        "invoice_id": invoice_id,
        "amount_usd": amount_usd,
        "approval_threshold_usd": threshold,
    }
    decision = interrupt(prompt)
    approved = bool(decision)
    return {
        "approval": approved,
        "hitl_prompt": prompt,
        "status": "cancelled" if not approved else "pending",
    }


def execute_payment_node(state: InvoiceReconciliationState) -> dict:
    """Execute payment if approved; otherwise no-op."""
    pending = state.get("pending_payment") or {}
    approved = state.get("approval", False)
    invoice_id = pending.get("invoice_id", "")
    amount_usd = Decimal(str(pending.get("amount", 0)))
    vendor_id = pending.get("vendor_id", "")
    result = execute_payment(invoice_id=invoice_id, amount_usd=amount_usd, vendor_id=vendor_id, approved=approved)
    return {"result": result, "status": result.get("status", "paid") if approved else "cancelled"}


def route_after_reconcile(state: InvoiceReconciliationState) -> str:
    """Manager: route to approval check or end (failed)."""
    if state.get("status") == "failed":
        return "__end__"
    if state.get("pending_payment"):
        return "check_approval"
    return "__end__"


def route_after_approval(state: InvoiceReconciliationState) -> str:
    """Route to execute payment or end (cancelled)."""
    if state.get("status") == "cancelled":
        return "__end__"
    return "execute_payment"


def build_graph(checkpointer):
    """Build the reconciliation graph with persistence and HITL."""
    builder = StateGraph(InvoiceReconciliationState)

    builder.add_node("reconcile", reconcile_node)
    builder.add_node("check_approval", check_approval_node)
    builder.add_node("execute_payment", execute_payment_node)

    builder.add_edge(START, "reconcile")
    builder.add_conditional_edges("reconcile", route_after_reconcile, {"check_approval": "check_approval", "__end__": END})
    builder.add_conditional_edges("check_approval", route_after_approval, {"execute_payment": "execute_payment", "__end__": END})
    builder.add_edge("execute_payment", END)

    return builder.compile(checkpointer=checkpointer)
</think>
Fixing the graph: correcting conditional edges and removing duplicates.
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
Read