"""App configuration and env. PII/cost settings live here."""

import os
from pathlib import Path

# Default DB path for state persistence (override with DB_PATH env for Docker)
_default_db = Path(__file__).resolve().parent.parent.parent / "data" / "checkpoints.db"
DEFAULT_DB_PATH = Path(os.getenv("DB_PATH", str(_default_db)))

# HITL: approve any payment above this amount (USD)
HITL_APPROVAL_THRESHOLD_USD = float(os.getenv("HITL_APPROVAL_THRESHOLD_USD", "5000"))

# Self-correction: max retries for failed tool calls
MAX_TOOL_RETRIES = int(os.getenv("MAX_TOOL_RETRIES", "3"))

# LLM (for cost control, use cheaper model by default)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

# PII: redact these keys in logs and API responses
PII_KEYS = {"vendor_tax_id", "bank_account", "vendor_email", "buyer_email"}
