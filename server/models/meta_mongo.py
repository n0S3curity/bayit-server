"""
meta_mongo.py — Per-list categories and suggestions collections.

categories doc:  { _id, listId, items: {"שיימורים": "שיימורים", ...} }
suggestions doc: { _id, listId, items: ["מדחום", "קורנפלקס", ...] }
"""

from db import get_collection

CATEGORIES_COL  = 'categories'
SUGGESTIONS_COL = 'suggestions'

DEFAULT_CATEGORIES = [
    'דברי חלב',
    'ירקות ופירות',
    'קפואים',
    'לחמים',
    'אפייה וקמחים',
    'מעדנייה',
    'שתיה',
    'חטיפים',
    'קטניות',
    'שימורים',
    'תינוקות',
    'חומרי ניקוי',
    'כלי בית',
    'חד פעמי',
    'פיצוחים',
    'תבלינים',
    'שונות',
    'כללי',
]


def _cat():
    return get_collection(CATEGORIES_COL)


def _sug():
    return get_collection(SUGGESTIONS_COL)


# ── Categories ────────────────────────────────────────────────────────────────

def get_categories(list_id) -> dict:
    """Return categories dict, e.g. {"שיימורים": "שיימורים", ...}"""
    doc = _cat().find_one({'listId': list_id})
    return doc.get('items', {}) if doc else {}


def seed_default_categories(list_id) -> None:
    """Bulk-insert all default categories for a newly created list."""
    items = {cat: cat for cat in DEFAULT_CATEGORIES}
    _cat().update_one(
        {'listId': list_id},
        {'$set': {'items': items}},
        upsert=True
    )


def add_category(list_id, category: str) -> None:
    """Add a category if it doesn't already exist."""
    _cat().update_one(
        {'listId': list_id},
        {'$set': {f'items.{category}': category}},
        upsert=True
    )


def category_exists(list_id, category: str) -> bool:
    doc = _cat().find_one({'listId': list_id})
    return doc is not None and category in doc.get('items', {})


# ── Suggestions ───────────────────────────────────────────────────────────────

def get_suggestions(list_id) -> list:
    """Return suggestions list."""
    doc = _sug().find_one({'listId': list_id})
    return doc.get('items', []) if doc else []


def add_suggestion(list_id, item_name: str) -> None:
    """Add a suggestion if it doesn't already exist (idempotent)."""
    _sug().update_one(
        {'listId': list_id},
        {'$addToSet': {'items': item_name}},
        upsert=True
    )
