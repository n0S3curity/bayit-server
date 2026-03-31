"""
security.py — Input sanitisation helpers for NoSQL injection defence.

MongoDB operators start with '$'. If user-supplied dicts reach a query
unfiltered, an attacker can inject operators like {"$gt": ""} to bypass
conditions.  These helpers strip such keys and coerce values to safe types
before they touch the database.
"""

from __future__ import annotations
from typing import Any


def sanitize(value: Any) -> Any:
    """
    Recursively remove any dict key that starts with '$'.
    Safe to call on arbitrary JSON-decoded input.
    """
    if isinstance(value, dict):
        return {k: sanitize(v) for k, v in value.items() if not k.startswith('$')}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    return value


def safe_str(value: Any, default: str = '') -> str:
    """
    Coerce *value* to a plain string.
    Rejects dicts and lists (potential operator injection vehicles).
    """
    if isinstance(value, (dict, list)):
        return default
    if value is None:
        return default
    return str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    """Coerce *value* to int; fall back to *default* on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
