"""
user_model.py — User collection helpers.

Document shape:
{
    "_id":          str,        # Firebase UID (Google sub)
    "email":        str,
    "displayName":  str,
    "photoURL":     str | None,
    "ownedLists":   [ObjectId, ...],
    "sharedLists":  [ObjectId, ...],
    "activeListId": ObjectId | None,
    "lastLogin":    datetime,
    "status":       "active" | "pending_list"
}
"""

from datetime import datetime, timezone
from db import get_collection

COLLECTION = 'users'

# ── Status constants ────────────────────────────────────────────────────────
STATUS_ACTIVE       = 'active'
STATUS_PENDING_LIST = 'pending_list'


def _col():
    return get_collection(COLLECTION)


# ── Factory ─────────────────────────────────────────────────────────────────

def build_user(uid: str, email: str, display_name: str, photo_url: str | None = None) -> dict:
    """Return a new user document (not yet saved)."""
    return {
        '_id':          uid,
        'email':        email,
        'displayName':  display_name,
        'photoURL':     photo_url,
        'ownedLists':   [],
        'sharedLists':  [],
        'activeListId': None,
        'lastLogin':    datetime.now(timezone.utc),
        'status':       STATUS_PENDING_LIST,
    }


# ── Read ─────────────────────────────────────────────────────────────────────

def get_by_uid(uid: str) -> dict | None:
    """Fetch a user by Firebase UID."""
    return _col().find_one({'_id': uid})


def get_by_email(email: str) -> dict | None:
    return _col().find_one({'email': email})


# ── Write ────────────────────────────────────────────────────────────────────

def upsert_on_login(uid: str, email: str, display_name: str, photo_url: str | None = None) -> dict:
    """
    Insert the user if new (status=pending_list), otherwise update
    displayName/photoURL/lastLogin.  Returns the up-to-date document.
    """
    existing = get_by_uid(uid)
    if existing is None:
        doc = build_user(uid, email, display_name, photo_url)
        _col().insert_one(doc)
        return doc

    _col().update_one(
        {'_id': uid},
        {'$set': {
            'displayName': display_name,
            'photoURL':    photo_url,
            'lastLogin':   datetime.now(timezone.utc),
        }}
    )
    return get_by_uid(uid)


def set_active_list(uid: str, list_id) -> None:
    """Set the user's currently active household list."""
    _col().update_one(
        {'_id': uid},
        {'$set': {'activeListId': list_id}}
    )


def set_status(uid: str, status: str) -> None:
    """Update user status (active / pending_list)."""
    if status not in (STATUS_ACTIVE, STATUS_PENDING_LIST):
        raise ValueError(f"Invalid status: {status!r}")
    _col().update_one({'_id': uid}, {'$set': {'status': status}})


def add_owned_list(uid: str, list_id) -> None:
    _col().update_one(
        {'_id': uid},
        {'$addToSet': {'ownedLists': list_id}}
    )


def remove_owned_list(uid: str, list_id) -> None:
    _col().update_one(
        {'_id': uid},
        {'$pull': {'ownedLists': list_id}}
    )


def add_shared_list(uid: str, list_id) -> None:
    _col().update_one(
        {'_id': uid},
        {'$addToSet': {'sharedLists': list_id}}
    )


def remove_shared_list(uid: str, list_id) -> None:
    _col().update_one(
        {'_id': uid},
        {'$pull': {'sharedLists': list_id}}
    )


# ── Validation helpers ────────────────────────────────────────────────────────

def user_has_access_to_list(uid: str, list_id) -> bool:
    """Return True if list_id is in the user's ownedLists OR sharedLists."""
    result = _col().find_one(
        {
            '_id': uid,
            '$or': [
                {'ownedLists': list_id},
                {'sharedLists': list_id},
            ]
        },
        {'_id': 1}
    )
    return result is not None


def count_user_lists(uid: str) -> int:
    """Return total number of lists (owned + shared) the user belongs to."""
    doc = _col().find_one({'_id': uid}, {'ownedLists': 1, 'sharedLists': 1})
    if not doc:
        return 0
    return len(doc.get('ownedLists', [])) + len(doc.get('sharedLists', []))
