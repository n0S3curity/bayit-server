"""
shopping_model.py — Shopping-list items collection helpers.

Document shape:
{
    "_id":      ObjectId,
    "listId":   ObjectId,  # household list
    "id":       int,        # numeric item ID (kept for app compat)
    "name":     str,
    "done":     bool,
    "quantity": int,
    "category": str
}
"""

from db import get_collection

COLLECTION = 'shopping_items'


def _col():
    return get_collection(COLLECTION)


# ── Read ──────────────────────────────────────────────────────────────────────

def get_items_dict(list_id) -> dict:
    """Return items as a dict keyed by str(id) — same shape as old list.json."""
    docs = list(_col().find({'listId': list_id}, {'_id': 0, 'listId': 0}))
    return {str(d['id']): d for d in docs}


def name_exists(list_id, name: str) -> bool:
    return _col().find_one({'listId': list_id, 'name': name}) is not None


def item_exists(list_id, item_id: int) -> bool:
    return _col().find_one({'listId': list_id, 'id': item_id}) is not None


# ── Write ─────────────────────────────────────────────────────────────────────

def add_item(list_id, item: dict) -> None:
    """Insert a new shopping item. item must already contain all required fields."""
    _col().insert_one({'listId': list_id, **item})


def remove_item(list_id, item_id: int) -> bool:
    result = _col().delete_one({'listId': list_id, 'id': item_id})
    return result.deleted_count > 0


def update_quantity(list_id, item_id: int, quantity: int) -> bool:
    result = _col().update_one(
        {'listId': list_id, 'id': item_id},
        {'$set': {'quantity': quantity}}
    )
    return result.matched_count > 0


def set_done(list_id, item_id: int, done: bool) -> bool:
    result = _col().update_one(
        {'listId': list_id, 'id': item_id},
        {'$set': {'done': done}}
    )
    return result.matched_count > 0
