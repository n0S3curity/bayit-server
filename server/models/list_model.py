"""
list_model.py — List (Household) collection helpers.

Document shape:
{
    "_id":         ObjectId,
    "name":        str,
    "ownerId":     str,         # Firebase UID of the owner
    "members":     [str, ...],  # Firebase UIDs (includes owner)
    "inviteToken": str,         # unique token for QR-code invitations
    "createdAt":   datetime
}
"""

import secrets
from datetime import datetime, timezone
from bson import ObjectId

from db import get_collection
import models.user_model as user_model
from models.meta_mongo import seed_default_categories

COLLECTION = 'lists'


def _col():
    return get_collection(COLLECTION)


# ── Factory ──────────────────────────────────────────────────────────────────

def _generate_invite_token() -> str:
    return secrets.token_urlsafe(24)


def build_list(name: str, owner_uid: str) -> dict:
    """Return a new list document (not yet saved)."""
    return {
        'name':        name.strip(),
        'ownerId':     owner_uid,
        'members':     [owner_uid],
        'inviteToken': _generate_invite_token(),
        'createdAt':   datetime.now(timezone.utc),
    }


# ── Create ────────────────────────────────────────────────────────────────────

def create_list(name: str, owner_uid: str) -> dict:
    """
    Create a new household list and wire it to the owner's user document.
    Returns the saved list document (with '_id').
    """
    doc = build_list(name, owner_uid)
    result = _col().insert_one(doc)
    list_id = result.inserted_id
    doc['_id'] = list_id

    # Update the owner's user document
    user_model.add_owned_list(owner_uid, list_id)
    user_model.set_active_list(owner_uid, list_id)
    user_model.set_status(owner_uid, user_model.STATUS_ACTIVE)

    # Seed default categories for the new list
    seed_default_categories(list_id)

    return doc


# ── Read ──────────────────────────────────────────────────────────────────────

def get_by_id(list_id) -> dict | None:
    if not isinstance(list_id, ObjectId):
        try:
            list_id = ObjectId(list_id)
        except Exception:
            return None
    return _col().find_one({'_id': list_id})


def get_by_invite_token(token: str) -> dict | None:
    return _col().find_one({'inviteToken': token})


def get_lists_for_user(uid: str) -> list[dict]:
    """Return all lists where the user is a member (owned + shared)."""
    return list(_col().find({'members': uid}))


# ── Mutations ─────────────────────────────────────────────────────────────────

def rename_list(list_id, new_name: str, requesting_uid: str) -> bool:
    """
    Both owner and members can rename a list.
    Returns True on success, False if the list was not found or user has no access.
    """
    if not isinstance(list_id, ObjectId):
        try:
            list_id = ObjectId(list_id)
        except Exception:
            return False

    result = _col().update_one(
        {'_id': list_id, 'members': requesting_uid},
        {'$set': {'name': new_name.strip()}}
    )
    return result.matched_count > 0


def regenerate_invite_token(list_id, requesting_uid: str) -> str | None:
    """Generate a fresh invite token. Only the owner may do this."""
    if not isinstance(list_id, ObjectId):
        try:
            list_id = ObjectId(list_id)
        except Exception:
            return None

    new_token = _generate_invite_token()
    result = _col().update_one(
        {'_id': list_id, 'ownerId': requesting_uid},
        {'$set': {'inviteToken': new_token}}
    )
    return new_token if result.matched_count > 0 else None


# ── Membership ────────────────────────────────────────────────────────────────

def join_by_token(token: str, uid: str) -> dict | None:
    """
    Add uid to the list identified by token.
    Returns the list document on success, None if token is invalid.
    The owner scanning their own token is a no-op (returns the list unchanged).
    """
    household = get_by_invite_token(token)
    if household is None:
        return None

    # Owner already belongs — nothing to change
    if household['ownerId'] == uid:
        return household

    list_id = household['_id']

    # Idempotent — no error if already a member
    _col().update_one(
        {'_id': list_id},
        {'$addToSet': {'members': uid}}
    )
    user_model.add_shared_list(uid, list_id)
    user_model.set_active_list(uid, list_id)
    user_model.set_status(uid, user_model.STATUS_ACTIVE)

    return get_by_id(list_id)


def leave_list(list_id, uid: str) -> tuple[bool, str]:
    """
    Remove a member from a list.
    Returns (success: bool, reason: str).

    Rules:
    - The owner cannot leave (they must delete the list or transfer ownership).
    - A user cannot leave their last list.
    """
    if not isinstance(list_id, ObjectId):
        try:
            list_id = ObjectId(list_id)
        except Exception:
            return False, 'invalid_list_id'

    household = get_by_id(list_id)
    if household is None:
        return False, 'not_found'

    if household['ownerId'] == uid:
        return False, 'owner_cannot_leave'

    if user_model.count_user_lists(uid) <= 1:
        return False, 'last_list'

    _col().update_one({'_id': list_id}, {'$pull': {'members': uid}})
    user_model.remove_shared_list(uid, list_id)

    # Switch active list to something else if this was the active one
    user = user_model.get_by_uid(uid)
    if user and str(user.get('activeListId')) == str(list_id):
        remaining = user.get('ownedLists', []) + user.get('sharedLists', [])
        remaining = [lid for lid in remaining if str(lid) != str(list_id)]
        new_active = remaining[0] if remaining else None
        user_model.set_active_list(uid, new_active)

    return True, 'ok'


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_list(list_id, requesting_uid: str) -> tuple[bool, str]:
    """
    Hard-delete a list and all its associated data.
    Only the owner can delete.
    A user cannot delete their last list without creating a new one first.

    Returns (success: bool, reason: str).
    """
    if not isinstance(list_id, ObjectId):
        try:
            list_id = ObjectId(list_id)
        except Exception:
            return False, 'invalid_list_id'

    household = get_by_id(list_id)
    if household is None:
        return False, 'not_found'

    if household['ownerId'] != requesting_uid:
        return False, 'not_owner'

    if user_model.count_user_lists(requesting_uid) <= 1:
        return False, 'last_list'

    # Cascade-delete ALL data scoped to this list
    from db import get_db
    database = get_db()
    for col_name in ('shopping_items', 'products', 'receipts', 'stats',
                     'categories', 'suggestions', 'settings'):
        database[col_name].delete_many({'listId': list_id})

    # Remove the list from every member's user document
    for member_uid in household.get('members', []):
        if member_uid == requesting_uid:
            user_model.remove_owned_list(member_uid, list_id)
        else:
            user_model.remove_shared_list(member_uid, list_id)

        # Update activeListId if this was their active list
        member = user_model.get_by_uid(member_uid)
        if member and str(member.get('activeListId')) == str(list_id):
            owned   = member.get('ownedLists', [])
            shared  = member.get('sharedLists', [])
            remaining = [l for l in owned + shared if str(l) != str(list_id)]
            user_model.set_active_list(member_uid, remaining[0] if remaining else None)

    _col().delete_one({'_id': list_id})
    return True, 'ok'
