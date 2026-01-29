"""Type-safe tools for invoice reconciliation (PydanticAI-style: Pydantic in/out)."""

import random
import time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from .config import HITL_APPROVAL_THRESHOLD_USD
from .models import Invoice, PurchaseOrder, ReconciliationResult

# ---- Tool input schemas (type-safe tool calling) ----


class FetchInvoicesInput(BaseModel):
    """Input for fetch_pending_invoices."""

    vendor_id: Optional[str] = Field(default=None, description="Filter by vendor ID, or all if omitted")
    limit: int = Field(default=10, ge=1, le=100, description="Max invoices to return")


class MatchInvoiceInput(BaseModel):
    """Input for match_invoice_to_po."""

    invoice_id: str = Field(description="Invoice to match")
    po_id: str = Field(description="Purchase order ID to match against")


class GetPaymentDetailsInput(BaseModel):
    """Input for get_payment_details (used before HITL)."""

    invoice_id: str = Field(description="Invoice ID")
    amount_usd: Decimal = Field(description="Amount in USD")


# ---- Mock data (replace with real API in production) ----


def _mock_invoices(vendor_id: Optional[str] = None, limit: int = 10) -> list[Invoice]:
    """Simulate ERP API: fetch pending invoices. Raises on simulated timeout."""
    # Simulate occasional timeout (for self-correction demo)
    if random.random() < 0.15:
        raise TimeoutError("ERP API timeout")
    items = [
        Invoice(
            invoice_id="INV-001",
            vendor_id="V001",
            vendor_name="Acme Corp",
            amount=Decimal("10000.00"),
            currency="USD",
            status="pending",
        ),
        Invoice(
            invoice_id="INV-002",
            vendor_id="V001",
            vendor_name="Acme Corp",
            amount=Decimal("500.00"),
            currency="USD",
            status="pending",
        ),
        Invoice(
            invoice_id="INV-003",
            vendor_id="V002",
            vendor_name="Beta Inc",
            amount=Decimal("2500.00"),
            currency="USD",
            status="pending",
        ),
    ]
    if vendor_id:
        items = [i for i in items if i.vendor_id == vendor_id]
    return items[:limit]


def _mock_pos() -> list[PurchaseOrder]:
    """Simulate PO system."""
    return [
        PurchaseOrder(po_id="PO-101", vendor_id="V001", total_amount=Decimal("10000.00"), status="open"),
        PurchaseOrder(po_id="PO-102", vendor_id="V001", total_amount=Decimal("500.00"), status="open"),
        PurchaseOrder(po_id="PO-201", vendor_id="V002", total_amount=Decimal("2500.00"), status="open"),
    ]


# ---- Tools (Pydantic in/out; can be used by PydanticAI agent or wrapped for LangGraph) ----


def fetch_pending_invoices(args: FetchInvoicesInput) -> list[dict]:
    """Fetch pending invoices from ERP. Optional vendor filter."""
    invoices = _mock_invoices(vendor_id=args.vendor_id, limit=args.limit)
    return [i.model_dump() for i in invoices]


def match_invoice_to_po(args: MatchInvoiceInput) -> ReconciliationResult:
    """Match an invoice to a purchase order; returns match score and amount match."""
    invoices = _mock_invoices(limit=100)
    pos = _mock_pos()
    inv = next((i for i in invoices if i.invoice_id == args.invoice_id), None)
    po = next((p for p in pos if p.po_id == args.po_id), None)
    if not inv or not po:
        return ReconciliationResult(
            invoice_id=args.invoice_id,
            po_id=args.po_id,
            match_score=0.0,
            amount_match=False,
            message="Invoice or PO not found",
        )
    amount_match = abs(inv.amount - po.total_amount) < Decimal("0.01")
    score = 1.0 if (inv.vendor_id == po.vendor_id and amount_match) else 0.5
    return ReconciliationResult(
        invoice_id=args.invoice_id,
        po_id=args.po_id,
        match_score=score,
        amount_match=amount_match,
        message="Match found" if score >= 0.5 else "No match",
    )


def get_payment_details(invoice_id: str, amount_usd: Decimal) -> dict:
    """Return payment summary for HITL approval (no PII in summary)."""
    return {
        "invoice_id": invoice_id,
        "amount_usd": str(amount_usd),
        "currency": "USD",
        "requires_approval": float(amount_usd) >= HITL_APPROVAL_THRESHOLD_USD,
        "approval_threshold_usd": HITL_APPROVAL_THRESHOLD_USD,
    }


def execute_payment(invoice_id: str, amount_usd: Decimal, vendor_id: str, approved: bool) -> dict:
    """Execute payment only if approved. Called after HITL."""
    if not approved:
        return {"status": "cancelled", "invoice_id": invoice_id, "reason": "User did not approve"}
    # Simulate payment API call
    time.sleep(0.1)
    return {
        "status": "paid",
        "invoice_id": invoice_id,
        "amount_usd": str(amount_usd),
        "vendor_id": vendor_id,
        "reference": f"PAY-{invoice_id}-{random.randint(1000, 9999)}",
    }
