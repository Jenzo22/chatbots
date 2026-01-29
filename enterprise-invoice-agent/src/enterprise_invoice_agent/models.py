"""Pydantic models for type-safe invoice reconciliation (PII-safe field names for demo)."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Invoice(BaseModel):
    """Invoice from ERP/AP system."""

    invoice_id: str = Field(description="Unique invoice identifier")
    vendor_id: str = Field(description="Vendor identifier")
    vendor_name: str = ""
    amount: Decimal = Field(description="Total amount in USD")
    currency: str = "USD"
    due_date: Optional[str] = None
    line_items: list[dict] = Field(default_factory=list)
    status: str = "pending"


class PurchaseOrder(BaseModel):
    """Purchase order for matching."""

    po_id: str = Field(description="Purchase order ID")
    vendor_id: str = ""
    total_amount: Decimal = Field(description="PO total in USD")
    status: str = "open"
    line_items: list[dict] = Field(default_factory=list)


class ReconciliationResult(BaseModel):
    """Result of matching an invoice to a PO."""

    invoice_id: str = ""
    po_id: str = ""
    match_score: float = Field(ge=0, le=1, description="0-1 match confidence")
    amount_match: bool = False
    message: str = ""


class PaymentRequest(BaseModel):
    """Request to execute payment (HITL approves this)."""

    invoice_id: str = ""
    amount: Decimal = Field(ge=0)
    currency: str = "USD"
    vendor_id: str = ""
    reference: str = ""
