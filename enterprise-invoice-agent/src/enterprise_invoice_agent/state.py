"""LangGraph state for invoice reconciliation workflow."""

from decimal import Decimal
from typing import Annotated, Literal, Optional, TypedDict

from operator import add


class InvoiceReconciliationState(TypedDict, total=False):
    """State for the reconciliation graph. Persisted by checkpointer."""

    # Input
    messages: Annotated[list, add]
    vendor_id: Optional[str]

    # Worker output
    reconciled: list
    pending_payment: Optional[dict]  # { invoice_id, amount, vendor_id } for HITL

    # HITL
    approval: Optional[bool]
    hitl_prompt: Optional[dict]  # JSON-serializable payload for interrupt()

    # Self-correction
    last_error: Optional[str]
    retry_count: int
    used_fallback: bool

    # Result
    status: Literal["pending", "awaiting_approval", "paid", "cancelled", "failed"]
    result: Optional[dict]
