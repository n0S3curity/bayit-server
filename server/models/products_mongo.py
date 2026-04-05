"""
products_mongo.py — Products collection helpers.

Document shape:
{
    "_id":            ObjectId,
    "listId":         ObjectId,
    "barcode":        str,
    "name":           str,
    "price":          float,
    "total_quantity": int,
    "total_price":    float,
    "favorite":       bool,
    "history":        [{"date": str, "quantity": int, "price": float}, ...],
    "cheapest_price": float,
    "highest_price":  float,
    "price_increase": float,
    "last_price":     float,
    "average_price":  float,
    "settings":       {"alias": str, "default_category": str}
}
"""

from db import get_collection

COLLECTION = 'products'


def _col():
    return get_collection(COLLECTION)


# ── Read ──────────────────────────────────────────────────────────────────────

def get_products_dict(list_id) -> dict:
    """Return all products as a dict keyed by barcode — same shape as old products.json."""
    docs = list(_col().find({'listId': list_id}, {'_id': 0, 'listId': 0}))
    return {d['barcode']: d for d in docs}


def get_products_paged(list_id, offset: int = 0, limit: int = 30, query: str = '') -> dict:
    """
    Return a page of products sorted by total_quantity descending.
    If query is given, filters by name or barcode (case-insensitive regex).
    Returns { items: [...], total: int, offset: int, limit: int }.
    """
    filter_q: dict = {'listId': list_id}
    if query:
        regex = {'$regex': query, '$options': 'i'}
        filter_q['$or'] = [{'name': regex}, {'barcode': regex}]

    col = _col()
    total = col.count_documents(filter_q)
    docs  = list(
        col.find(filter_q, {'_id': 0, 'listId': 0})
           .sort('total_quantity', -1)
           .skip(offset)
           .limit(limit)
    )
    return {'items': docs, 'total': total, 'offset': offset, 'limit': limit}


def get_product(list_id, barcode: str) -> dict | None:
    """Fetch a single product, stripping Mongo internals."""
    doc = _col().find_one(
        {'listId': list_id, 'barcode': barcode},
        {'_id': 0, 'listId': 0}
    )
    return doc


def get_all_for_processing(list_id) -> dict:
    """
    Load all products as a barcode→dict map for in-memory processing.
    Includes _id so that bulk_save_products can do targeted upserts.
    """
    return {d['barcode']: d for d in _col().find({'listId': list_id})}


# ── Write ─────────────────────────────────────────────────────────────────────

def set_favorite(list_id, barcode: str, value: bool) -> bool:
    result = _col().update_one(
        {'listId': list_id, 'barcode': barcode},
        {'$set': {'favorite': value}}
    )
    return result.matched_count > 0


def get_regular_basket(list_id) -> dict:
    """
    Return the top 30% of products ranked by purchase frequency:
    how many distinct receipt visits contained this product (len(history)).

    A product bought in every trip scores 100%; one bought once scores low.
    TOP 30% of distinct products by visit_count are the "regular basket".

    Returns:
        {
            items: [{ ...product, visit_count, visit_pct }, ...],
            total_products: int,
            basket_size: int,
            total_receipts: int,
        }
    """
    import math
    from db import get_collection

    # Total distinct receipts for this list
    receipts_col = get_collection('receipts')
    total_receipts = receipts_col.count_documents({'listId': list_id})

    col = _col()
    docs = list(col.find({'listId': list_id}, {'_id': 0, 'listId': 0}))

    # Annotate each product with visit_count = number of history entries
    # (each entry represents one receipt/visit)
    for doc in docs:
        history = doc.get('history') or []
        visit_count = len(history)
        doc['visit_count'] = visit_count
        doc['visit_pct'] = round(
            (visit_count / total_receipts * 100) if total_receipts > 0 else 0,
            1
        )

    # Sort by visit frequency descending, then by total_quantity as tiebreaker
    docs.sort(key=lambda d: (d['visit_count'], d.get('total_quantity', 0)), reverse=True)

    total_products = len(docs)
    basket_size = math.ceil(total_products * 0.20) if total_products > 0 else 0

    return {
        'items': docs[:basket_size],
        'total_products': total_products,
        'basket_size': basket_size,
        'total_receipts': total_receipts,
    }


def bulk_upsert(list_id, products: dict) -> None:
    """
    Upsert all products from a barcode→data dict.
    Used after in-memory receipt processing.
    """
    from pymongo import UpdateOne
    if not products:
        return
    ops = [
        UpdateOne(
            {'listId': list_id, 'barcode': barcode},
            {'$set': {**data, 'listId': list_id, 'barcode': barcode}},
            upsert=True
        )
        for barcode, data in products.items()
    ]
    _col().bulk_write(ops, ordered=False)
