import os
from functools import wraps

import firebase_admin
from firebase_admin import credentials, auth
from flask import g, jsonify, request

# Guard against double-init (Flask debug reloader re-imports modules)
if not firebase_admin._apps:
    service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
    if service_account_path:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
    else:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_PATH environment variable is not set. "
            "Set it to the path of your Firebase service account JSON file."
        )


def require_auth(f):
    """
    Decorator that verifies the Firebase ID token in the Authorization header
    and injects two Flask-g values:

        g.user    — decoded Firebase token dict  (uid, email, …)
        g.list_id — the user's active household ObjectId, or None if not set
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        token = auth_header.split(' ', 1)[1]
        try:
            decoded = auth.verify_id_token(token)
            g.user = decoded  # uid and email available as g.user['uid'], g.user['email']
        except Exception:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Resolve the active list for this request and verify ownership
        try:
            from models.user_model import get_by_uid, set_active_list
            user_doc = get_by_uid(decoded['uid'])
            if user_doc:
                active = user_doc.get('activeListId')
                if active:
                    # Verify the user still has access to this list (may have
                    # been removed from the household since the token was issued)
                    allowed = set(
                        str(lid) for lid in
                        user_doc.get('ownedLists', []) + user_doc.get('sharedLists', [])
                    )
                    if str(active) not in allowed:
                        # Stale activeListId — clear it so the app prompts re-selection
                        set_active_list(decoded['uid'], None)
                        active = None
                g.list_id = active
            else:
                g.list_id = None
        except Exception:
            # MongoDB may not be reachable yet during startup — degrade gracefully
            g.list_id = None

        return f(*args, **kwargs)
    return decorated


def _no_active_list():
    return jsonify({'error': 'No active list. Please create or join a household first.'}), 400


def require_list(f):
    """
    Stack on top of @require_auth to enforce that g.list_id is set.
    Returns 400 if the user has no active list (status=pending_list).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(g, 'list_id', None):
            return _no_active_list()
        return f(*args, **kwargs)
    return decorated
