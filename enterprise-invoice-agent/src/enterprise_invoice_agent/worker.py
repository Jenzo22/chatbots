"""Worker: type-safe tool execution (PydanticAI-style tools) with self-correction wrapper."""

from decimal import Decimal

from .config import MAX_TOOL_RETRIES
from .tools import (
    FetchInvoicesInput,
    MatchInvoiceInput,
    fetch_pending_invoices,
    get_payment_details,
    match_invoice_to_po,
)
from .models import ReconciliationResult


def run_fetch_invoices(vendor_id: str | None = None, limit: int = 10) -> list[dict]:
    """Call fetch_pending_invoices with type-safe input. Used by graph with retry."""
    inp = FetchInvoicesInput(vendor_id=vendor_id, limit=limit)
    return fetch_pending_invoices(inp)


def run_match_invoice(invoice_id: str, po_id: str) -> ReconciliationResult:
    """Call match_invoice_to_po with type-safe input."""
    inp = MatchInvoiceInput(invoice_id=invoice_id, po_id=po_id)
    return match_invoice_to_po(inp)


def run_with_retry_and_fallback(fn, *args, fallback_result=None, max_retries: int = MAX_TOOL_RETRIES, **kwargs):
    """
    Self-correction loop: retry on failure, then return fallback if all retries fail.
    Returns (result, error, used_fallback).
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            result = fn(*args, **kwargs)
            return result, None, False
        except Exception as e:
            last_error = e
            if attempt == max_retries - 1:
                return fallback_result, last_error, True
    return fallback_result, last_error, True


def reconcile_step(vendor_id: str | None, limit: int = 5) -> tuple[list[dict], Exception | None, bool]:
    """
    One reconciliation step: fetch invoices with retry/fallback, then match first to a PO.
    Returns (list of reconciled items with match result, error if any, used_fallback).
    """
    fallback_invoices = []  # empty list as fallback so graph can decide next
    invoices, err, used_fallback = run_with_retry_and_fallback(
        run_fetch_invoices, vendor_id=vendor_id, limit=limit, fallback_result=fallback_invoices
    )
    if err:
        return [], err, used_fallback
    reconciled = []
    for inv in (invoices or [])[:3]:
        inv_id = inv.get("invoice_id", "")
        # Match to a default PO for demo (in production, worker or LLM would pick PO)
        vid = inv.get("vendor_id") or ""
        po_id = "PO-101" if vid == "V001" else ("PO-201" if vid == "V002" else "PO-101")
        try:
            match = run_match_invoice(inv_id, po_id)
            reconciled.append({"invoice": inv, "match": match.model_dump()})
        except Exception as e:
            reconciled.append({"invoice": inv, "match": None, "error": str(e)})
    return reconciled, None, used_fallback


def get_payment_summary(invoice_id: str, amount_usd: Decimal) -> dict:
    """Get payment details for HITL approval prompt."""
    return get_payment_details(invoice_id, amount_usd)
