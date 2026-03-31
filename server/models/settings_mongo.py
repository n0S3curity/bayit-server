"""
settings_mongo.py — Per-list general settings (liked supermarkets).

MongoDB stores only the mutable part (liked) per list:
    { _id, listId, liked: {"osherad": [...], "yohananof": [...]} }

The static `available` list is read from the local general_settings.json
file (initialised by create_db_files() at startup) and merged at read time.
This avoids duplicating the large static dataset in every list document.
"""

import json
import os

from db import get_collection

COLLECTION = 'settings'

# Path to the static supermarkets data file (populated once by create_db_files)
_SETTINGS_FILE = os.path.join(
    os.path.dirname(__file__), '..', '..', 'databases', 'general_settings.json'
)


def _col():
    return get_collection(COLLECTION)


def _load_static_available() -> dict:
    """Read the available supermarkets from the static JSON file."""
    try:
        with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('supermarkets', {}).get('available', {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ── Read ──────────────────────────────────────────────────────────────────────

def get_liked(list_id) -> dict:
    """Return just the liked supermarkets dict for a list."""
    doc = _col().find_one({'listId': list_id})
    if doc:
        return doc.get('liked', {})
    # Initialise with empty liked section on first access
    default_liked = {"yohananof": [], "osherad": []}
    _col().insert_one({'listId': list_id, 'liked': default_liked})
    return default_liked


def get_full_settings(list_id) -> dict:
    """
    Return the full generalSettings structure expected by the app:
    { "supermarkets": { "liked": {...}, "available": {...} } }
    """
    liked     = get_liked(list_id)
    available = _load_static_available()
    return {"supermarkets": {"liked": liked, "available": available}}


# ── Write ─────────────────────────────────────────────────────────────────────

def add_liked_store(list_id, brand_name: str, store: dict) -> tuple[bool, str]:
    """
    Add a store to the liked list.
    Returns (success, reason).
    """
    liked = get_liked(list_id)
    brand_stores = liked.get(brand_name, [])

    if any(str(s.get('StoreId')) == str(store['StoreId']) for s in brand_stores):
        return False, 'already_exists'

    _col().update_one(
        {'listId': list_id},
        {'$push': {f'liked.{brand_name}': store}},
        upsert=True
    )
    return True, 'ok'


def remove_liked_store(list_id, brand_name: str, store_id) -> tuple[bool, str]:
    """
    Remove a store from the liked list by StoreId.
    Returns (success, reason).
    """
    liked = get_liked(list_id)
    brand_stores = liked.get(brand_name)
    if brand_stores is None:
        return False, 'brand_not_found'

    # Find the matching store doc (StoreId can be str or int)
    matching = next(
        (s for s in brand_stores if str(s.get('StoreId')) == str(store_id)),
        None
    )
    if matching is None:
        return False, 'store_not_found'

    _col().update_one(
        {'listId': list_id},
        {'$pull': {f'liked.{brand_name}': {'StoreId': matching['StoreId']}}}
    )
    return True, 'ok'
