# list_routes.py — Phase 3: Auth session, household list management, invitations
from bson import ObjectId
from flask import Blueprint, g, jsonify, request

from auth_middleware import require_auth, require_list
from extensions import limiter
from security import safe_str
from models.user_model import (
    upsert_on_login,
    get_by_uid,
    set_active_list,
    user_has_access_to_list,
)
from models.list_model import (
    create_list,
    get_by_id,
    get_lists_for_user,
    rename_list,
    delete_list,
    leave_list,
    join_by_token,
    regenerate_invite_token,
)

list_bp = Blueprint('lists', __name__, url_prefix='/api')


# ── Serialisation helpers ─────────────────────────────────────────────────────

def _ser_list(doc: dict, uid: str | None = None) -> dict:
    """
    Convert a lists-collection document to a JSON-safe dict.
    Does NOT expose inviteToken — use the /invite endpoint for that.
    """
    created_at = doc.get('createdAt')
    return {
        'id':          str(doc['_id']),
        'name':        doc['name'],
        'ownerId':     doc['ownerId'],
        'members':     doc.get('members', []),
        'memberCount': len(doc.get('members', [])),
        'isOwner':     uid is not None and uid == doc['ownerId'],
        'createdAt':   created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at or ''),
    }


def _ser_user(doc: dict) -> dict:
    """Return a JSON-safe user profile (no internal Mongo fields)."""
    active = doc.get('activeListId')
    return {
        'uid':          doc['_id'],
        'email':        doc.get('email', ''),
        'displayName':  doc.get('displayName', ''),
        'photoURL':     doc.get('photoURL'),
        'status':       doc.get('status', 'active'),
        'activeListId': str(active) if active else None,
    }


def _parse_list_id(raw: str):
    """Parse a string into ObjectId, returning None on failure."""
    try:
        return ObjectId(raw)
    except Exception:
        return None


# ── Auth ──────────────────────────────────────────────────────────────────────

@list_bp.route('/auth/login', methods=['POST'])
@limiter.limit("20 per minute")
@require_auth
def login():
    """
    Called by the app immediately after Firebase sign-in.

    - Creates the user document if it's their first login (status=pending_list).
    - Updates displayName / photoURL / lastLogin on subsequent logins.

    Response:
        {
            status:  "active" | "pending_list",
            user:    { uid, email, displayName, photoURL, activeListId },
            lists:   [ list, ... ]          # empty when status=pending_list
        }
    """
    uid          = g.user['uid']
    email        = g.user.get('email', '')
    display_name = g.user.get('name') or g.user.get('email', '')
    photo_url    = g.user.get('picture')

    user = upsert_on_login(uid, email, display_name, photo_url)
    lists = get_lists_for_user(uid)

    return jsonify({
        'status': user['status'],
        'user':   _ser_user(user),
        'lists':  [_ser_list(l, uid) for l in lists],
    }), 200


# ── Household list management ─────────────────────────────────────────────────

@list_bp.route('/lists', methods=['GET'])
@require_auth
def get_user_lists():
    """Return all lists (owned + shared) for the authenticated user."""
    uid   = g.user['uid']
    lists = get_lists_for_user(uid)
    return jsonify([_ser_list(l, uid) for l in lists]), 200


@list_bp.route('/lists', methods=['POST'])
@require_auth
def create_new_list():
    """
    Create a new household list.

    Body: { "name": "My Household" }

    Also used as the mandatory first step for a pending_list user:
    the server sets their status to active and activeListId to the new list.
    """
    uid  = g.user['uid']
    name = safe_str((request.get_json() or {}).get('name', ''))
    if not name:
        return jsonify({'error': 'List name is required.'}), 400

    household = create_list(name, uid)
    return jsonify({
        'message': 'List created.',
        'list':    _ser_list(household, uid),
    }), 201


@list_bp.route('/lists/active', methods=['GET'])
@require_auth
@require_list
def get_active_list():
    """Return the currently active household list."""
    household = get_by_id(g.list_id)
    if not household:
        return jsonify({'error': 'Active list not found.'}), 404
    return jsonify(_ser_list(household, g.user['uid'])), 200


@list_bp.route('/lists/<list_id>/switch', methods=['POST'])
@require_auth
def switch_active_list(list_id):
    """Switch the caller's active list. They must already be a member."""
    uid = g.user['uid']
    oid = _parse_list_id(list_id)
    if oid is None:
        return jsonify({'error': 'Invalid list ID.'}), 400

    if not user_has_access_to_list(uid, oid):
        return jsonify({'error': 'You are not a member of this list.'}), 403

    set_active_list(uid, oid)
    household = get_by_id(oid)
    return jsonify({
        'message': 'Active list switched.',
        'list':    _ser_list(household, uid),
    }), 200


@list_bp.route('/lists/<list_id>/name', methods=['PUT'])
@require_auth
def rename_list_endpoint(list_id):
    """
    Rename a list. Both owner and members may rename.

    Body: { "name": "New Name" }
    """
    uid      = g.user['uid']
    new_name = safe_str((request.get_json() or {}).get('name', ''))
    if not new_name:
        return jsonify({'error': 'Name is required.'}), 400

    if not rename_list(list_id, new_name, uid):
        return jsonify({'error': 'List not found or access denied.'}), 404

    household = get_by_id(_parse_list_id(list_id))
    return jsonify({
        'message': 'List renamed.',
        'list':    _ser_list(household, uid),
    }), 200


@list_bp.route('/lists/<list_id>', methods=['DELETE'])
@require_auth
def delete_list_endpoint(list_id):
    """
    Permanently delete a list and all its data. Owner only.
    The owner must have at least one other list before deleting this one.
    """
    success, reason = delete_list(list_id, g.user['uid'])
    if not success:
        messages = {
            'not_owner':       ('Only the owner can delete a list.', 403),
            'last_list':       ('Cannot delete your only list. Create a new one first.', 400),
            'not_found':       ('List not found.', 404),
            'invalid_list_id': ('Invalid list ID.', 400),
        }
        msg, code = messages.get(reason, (reason, 400))
        return jsonify({'error': msg}), code

    return jsonify({'message': 'List deleted.'}), 200


@list_bp.route('/lists/<list_id>/leave', methods=['POST'])
@require_auth
def leave_list_endpoint(list_id):
    """
    Leave a list. Only non-owner members may leave.
    The user must have at least one other list before leaving.
    """
    success, reason = leave_list(list_id, g.user['uid'])
    if not success:
        messages = {
            'owner_cannot_leave': ('The owner cannot leave. Delete the list or transfer ownership first.', 400),
            'last_list':          ('Cannot leave your only list. Join or create another first.', 400),
            'not_found':          ('List not found.', 404),
            'invalid_list_id':    ('Invalid list ID.', 400),
        }
        msg, code = messages.get(reason, (reason, 400))
        return jsonify({'error': msg}), code

    return jsonify({'message': 'Left the list successfully.'}), 200


# ── Invitations ───────────────────────────────────────────────────────────────

@list_bp.route('/lists/<list_id>/invite', methods=['GET'])
@require_auth
def get_invite(list_id):
    """
    Return the invite token for a list.
    Any member (owner or shared) may retrieve it to share the QR.

    Response: { token, joinUrl }
    joinUrl is a deep-link the mobile app turns into a QR code.
    """
    uid = g.user['uid']
    oid = _parse_list_id(list_id)
    if oid is None:
        return jsonify({'error': 'Invalid list ID.'}), 400

    household = get_by_id(oid)
    if not household:
        return jsonify({'error': 'List not found.'}), 404

    if uid not in household.get('members', []):
        return jsonify({'error': 'Access denied.'}), 403

    token = household.get('inviteToken', '')
    return jsonify({
        'token':   token,
        'joinUrl': f"bayit://join/{token}",
    }), 200


@list_bp.route('/lists/<list_id>/invite/refresh', methods=['POST'])
@limiter.limit("5 per minute")
@require_auth
def refresh_invite(list_id):
    """
    Generate a fresh invite token, invalidating the previous one.
    Owner only.

    Response: { token, joinUrl }
    """
    uid       = g.user['uid']
    new_token = regenerate_invite_token(list_id, uid)
    if new_token is None:
        return jsonify({'error': 'List not found or you are not the owner.'}), 403

    return jsonify({
        'token':   new_token,
        'joinUrl': f"bayit://join/{new_token}",
    }), 200


@list_bp.route('/lists/join', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
def join_list():
    """
    Join a household by invite token (scanned from QR or shared as text).

    Body: { "token": "<inviteToken>" }

    Response: { message, list, user }
    """
    uid   = g.user['uid']
    token = safe_str((request.get_json() or {}).get('token', ''))
    if not token:
        return jsonify({'error': 'Invite token is required.'}), 400

    household = join_by_token(token, uid)
    if household is None:
        return jsonify({'error': 'Invalid or expired invite token.'}), 404

    # Return fresh user doc so app can update activeListId
    user = get_by_uid(uid)
    return jsonify({
        'message': 'Joined household successfully.',
        'list':    _ser_list(household, uid),
        'user':    _ser_user(user),
    }), 200
