"""
PydanticAI agent with type-safe tools for invoice reconciliation.
Use this when you want an LLM to decide which tools to call; the graph uses the same
tools directly (worker.py) for deterministic retry/fallback without LLM cost.
"""

from pydantic_ai import Agent

from .tools import (
    FetchInvoicesInput,
    MatchInvoiceInput,
    fetch_pending_invoices,
    match_invoice_to_po,
)


def _fetch_invoices(vendor_id: str | None = None, limit: int = 10) -> str:
    """Fetch pending invoices (type-safe input)."""
    inp = FetchInvoicesInput(vendor_id=vendor_id, limit=limit)
    result = fetch_pending_invoices(inp)
    return str(result)


def _match_invoice(invoice_id: str, po_id: str) -> str:
    """Match an invoice to a PO (type-safe input)."""
    inp = MatchInvoiceInput(invoice_id=invoice_id, po_id=po_id)
    result = match_invoice_to_po(inp)
    return result.model_dump_json()


# Type-safe tool calling: Pydantic inputs (FetchInvoicesInput, MatchInvoiceInput) used by tools.
reconciliation_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="You help reconcile invoices. Use fetch_invoices to get pending invoices and match_invoice to match them to POs.",
    tools=[_fetch_invoices, _match_invoice],
)
