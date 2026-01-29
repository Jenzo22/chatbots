"""Security: PII filtering for logs and API responses."""

from typing import Any

from .config import PII_KEYS

REDACT_PLACEHOLDER = "[REDACTED]"


def redact_pii(obj: Any) -> Any:
    """Recursively redact known PII keys from dicts/lists. Used for logs and responses."""
    if isinstance(obj, dict):
        return {
            k: REDACT_PLACEHOLDER if k in PII_KEYS else redact_pii(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [redact_pii(item) for item in obj]
    return obj
