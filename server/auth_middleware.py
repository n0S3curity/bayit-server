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
    """Decorator that verifies the Firebase ID token in the Authorization header."""
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
        return f(*args, **kwargs)
    return decorated
