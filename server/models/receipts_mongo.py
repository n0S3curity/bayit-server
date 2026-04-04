"""
receipts_mongo.py — Receipts metadata collection helpers.

Document shape:
{
    "_id":         ObjectId,
    "listId":      ObjectId,
    "originalLink": str,        # Pairzon URL — used for duplicate prevention
    "scannedAt":   datetime,
    "company":     str,         # "osherad" | "yohananof"
    "cityEnglish": str,         # English city slug (for PDF file lookup)
    "receiptId":   str,         # filename without extension (e.g. "0309250025139198")
    "total":       float,
    "createdDate": str          # "2025-09-03 18:43:45"
}
"""

from datetime import datetime, timezone

from db import get_collection

COLLECTION = 'receipts'


def _col():
    return get_collection(COLLECTION)


# ── Read ──────────────────────────────────────────────────────────────────────

def link_exists(list_id, original_link: str) -> bool:
    """Return True if this link was already processed for the given list."""
    return _col().find_one(
        {'listId': list_id, 'originalLink': original_link},
        {'_id': 1}
    ) is not None


def receipt_belongs_to_list(list_id, receipt_id: str) -> bool:
    """Return True if receipt_id was scanned by this list."""
    return _col().find_one(
        {'listId': list_id, 'receiptId': receipt_id},
        {'_id': 1}
    ) is not None


def get_receipts_for_list(list_id) -> list[dict]:
    """Return all receipt metadata docs for a list (without Mongo internals)."""
    return list(_col().find(
        {'listId': list_id},
        {'_id': 0, 'listId': 0}
    ))


# ── Write ─────────────────────────────────────────────────────────────────────

def save_receipt(
    list_id,
    original_link: str,
    company: str,
    city_english: str,
    receipt_id: str,
    total: float,
    created_date: str,
    items: list | None = None,
) -> None:
    """Insert a new receipt metadata document."""
    _col().insert_one({
        'listId':       list_id,
        'originalLink': original_link,
        'scannedAt':    datetime.now(timezone.utc),
        'company':      company,
        'cityEnglish':  city_english,
        'receiptId':    receipt_id,
        'total':        total,
        'createdDate':  created_date,
        'items':        items or [],
    })


def get_receipt_by_id(list_id, receipt_id: str) -> dict | None:
    """Return a single receipt document (without Mongo internals)."""
    return _col().find_one(
        {'listId': list_id, 'receiptId': receipt_id},
        {'_id': 0, 'listId': 0}
    )
