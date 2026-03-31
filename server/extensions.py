"""
extensions.py — Flask extension singletons.

Initialised here so that api_routes, list_routes, etc. can all import
the same `limiter` object without circular imports.  Call
`limiter.init_app(app)` in app.py after the app is created.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["300 per minute"],
    storage_uri="memory://",
)
