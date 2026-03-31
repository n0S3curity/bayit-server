"""
db.py — MongoDB connection singleton.

Usage:
    from db import get_db, get_collection

    db = get_db()
    users = get_collection('users')
"""

import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

_client: MongoClient | None = None


def get_client() -> MongoClient:
    """Return (and lazily create) the shared MongoClient."""
    global _client
    if _client is None:
        uri = os.environ.get('MONGODB_URI')
        if not uri:
            raise RuntimeError(
                "MONGODB_URI environment variable is not set. "
                "Add it to your .env file."
            )
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Fail fast on startup if the server is unreachable
        try:
            _client.admin.command('ping')
        except ConnectionFailure as e:
            _client = None
            raise RuntimeError(f"MongoDB connection failed: {e}") from e
    return _client


def get_db():
    """Return the application database."""
    db_name = os.environ.get('MONGODB_DB', 'bayit')
    return get_client()[db_name]


def get_collection(name: str):
    """Convenience accessor: get_collection('users')."""
    return get_db()[name]


def init_indexes():
    """
    Create all indexes required by the application.
    Safe to call multiple times (MongoDB ignores duplicate index creation).
    Call once at app startup from app.py.
    """
    db = get_db()

    # ── Users ──────────────────────────────────────────────────────────────
    users = db['users']
    users.create_index([('email', ASCENDING)], unique=True, name='email_unique')

    # ── Lists ──────────────────────────────────────────────────────────────
    lists = db['lists']
    lists.create_index([('ownerId', ASCENDING)], name='lists_by_owner')
    lists.create_index([('members', ASCENDING)], name='lists_by_member')
    lists.create_index(
        [('inviteToken', ASCENDING)],
        unique=True,
        sparse=True,        # documents without the field are excluded
        name='invite_token_unique'
    )

    # ── Receipts ───────────────────────────────────────────────────────────
    receipts = db['receipts']
    receipts.create_index([('listId', ASCENDING)], name='receipts_by_list')
    receipts.create_index(
        [('listId', ASCENDING), ('originalLink', ASCENDING)],
        unique=True,
        name='receipts_link_per_list'
    )

    # ── Shopping Lists ─────────────────────────────────────────────────────
    shopping_items = db['shopping_items']
    shopping_items.create_index([('listId', ASCENDING)], name='items_by_list')

    # ── Products ───────────────────────────────────────────────────────────
    products = db['products']
    products.create_index(
        [('listId', ASCENDING), ('barcode', ASCENDING)],
        unique=True,
        name='products_per_list'
    )
