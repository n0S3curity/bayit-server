# api_routes.py
import os
import traceback
from urllib.parse import urlparse, parse_qs

import requests
from flask import Blueprint, g, send_file
from flask import request, jsonify

from helpers import (
    generate_item_id,
    generate_receipt_filename,
    get_hebrew_city_name,
    process_receipt_mongo,
)
from auth_middleware import require_auth, require_list
from extensions import limiter
from security import safe_str, safe_int
from models.shopping_model import (
    get_items_dict,
    name_exists as item_name_exists,
    add_item,
    remove_item,
    update_quantity,
    set_done,
)
from models.meta_mongo import (
    get_categories,
    add_category,
    category_exists,
    get_suggestions,
    add_suggestion,
)
from models.products_mongo import (
    get_products_dict,
    get_products_paged,
    get_product,
    get_regular_basket,
    set_favorite,
)
from models.settings_mongo import (
    get_full_settings,
    get_liked,
    add_liked_store,
    remove_liked_store,
    _load_static_available,
)
from models.receipts_mongo import (
    link_exists as receipt_link_exists,
    manual_receipt_number_exists,
    get_receipts_for_list,
    save_receipt,
    receipt_belongs_to_list,
    get_receipt_by_id,
)

api_bp = Blueprint('api', __name__, url_prefix='/api')

_KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), 'insight_keywords.json')


# ── Insight keywords ──────────────────────────────────────────────────────────

@api_bp.route('/insight-keywords', methods=['GET'])
@require_auth
def get_insight_keywords():
    """Return the keyword lists used by the client-side insights engine."""
    import json
    try:
        with open(_KEYWORDS_PATH, encoding='utf-8') as f:
            data = json.load(f)
        # Strip internal comment key before sending
        data.pop('_comment', None)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({}), 200


# ── Shopping list ─────────────────────────────────────────────────────────────

@api_bp.route('/list', methods=['GET'])
@require_auth
@require_list
def get_shopping_list():
    list_id = g.list_id
    shopping_list = get_items_dict(list_id)
    shopping_list['categories'] = get_categories(list_id)
    shopping_list['suggestions'] = get_suggestions(list_id)
    return jsonify(shopping_list)


@api_bp.route('/list/add', methods=['POST'])
@require_auth
@require_list
def add_item_to_list():
    list_id  = g.list_id
    body     = request.get_json()
    item_name = safe_str(body.get('item', ''))
    quantity  = safe_int(body.get('quantity', 1), default=1)
    category  = safe_str(body.get('category', 'כללי')) or 'כללי'

    if item_name_exists(list_id, item_name):
        return jsonify({"error": f"Item already exists in the list."}), 400

    if not category_exists(list_id, category):
        add_category(list_id, category)

    add_suggestion(list_id, item_name)

    item = {
        "id":       generate_item_id(),
        "name":     item_name,
        "done":     False,
        "quantity": quantity,
        "category": category,
    }
    add_item(list_id, item)

    return jsonify({"message": f"Item '{item['id']}' added to the list."}), 201


@api_bp.route('/list/remove', methods=['POST'])
@require_auth
@require_list
def remove_product_from_list():
    list_id = g.list_id
    item_id = int(request.get_json()['itemID'])
    if not remove_item(list_id, item_id):
        return jsonify({"error": "Item not found in the list."}), 404
    return jsonify({"message": "Item removed from the list."}), 200


@api_bp.route('/list/quantity', methods=['POST'])
@require_auth
@require_list
def change_product_quantity():
    list_id      = g.list_id
    body         = request.get_json()
    item_id      = int(body['itemID'])
    new_quantity = body['quantity']
    if not isinstance(new_quantity, int) or new_quantity < 0:
        return jsonify({"error": "Quantity must be a non-negative integer."}), 400
    if not update_quantity(list_id, item_id, new_quantity):
        return jsonify({"error": "Item not found in the list."}), 404
    return jsonify({"message": f"Quantity for item '{item_id}' updated to {new_quantity}."}), 200


@api_bp.route('/list/done', methods=['POST'])
@require_auth
@require_list
def set_item_as_done():
    list_id = g.list_id
    item_id = int(str(request.get_json()['itemID']))
    print(f"Incoming itemID: {item_id}")
    if not set_done(list_id, item_id, True):
        print(f"DEBUG: Item ID '{item_id}' not found in list, returning 404.")
        return jsonify({"error": "Item not found in the list."}), 404
    print(f"DEBUG: Item ID '{item_id}' marked as done, returning 200.")
    return jsonify({"message": "Item marked as done."}), 200


@api_bp.route('/list/undone', methods=['POST'])
@require_auth
@require_list
def set_item_as_undone():
    list_id = g.list_id
    item_id = int(request.get_json()['itemID'])
    if not set_done(list_id, item_id, False):
        return jsonify({"error": "Item not found in the list."}), 404
    return jsonify({"message": "Item marked as undone."}), 200


# ── General settings ──────────────────────────────────────────────────────────

@api_bp.route('/generalSettings', methods=['GET'])
@require_auth
@require_list
def get_general_settings():
    try:
        settings = get_full_settings(g.list_id)
        return jsonify(settings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/generalSettings/remove', methods=['POST'])
@require_auth
@require_list
def remove_general_setting():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON."}), 400
    if 'StoreId' not in request.json:
        return jsonify({"error": "storeId is required."}), 400
    store_id = safe_str(request.json.get('StoreId', ''))
    if not store_id:
        return jsonify({"error": "storeId cannot be empty."}), 400
    brand_name = safe_str(request.json.get('brandName', '')).lower()
    if not brand_name:
        return jsonify({"error": "brandName is required."}), 400

    success, reason = remove_liked_store(g.list_id, brand_name, store_id)
    if not success:
        if reason == 'store_not_found':
            return jsonify({"error": f"Store {store_id} not found in liked settings."}), 404
        return jsonify({"error": reason}), 400
    return jsonify({"message": f"Store {store_id} removed from liked settings."}), 200


@api_bp.route('/generalSettings/add', methods=['POST'])
@require_auth
@require_list
def add_general_setting():
    store_id   = safe_str(request.json.get('StoreId', ''))
    brand_name = safe_str(request.json.get('brandName', '')).lower()
    print(f"Received StoreId: {store_id}, brandName: {brand_name}")

    available  = _load_static_available()
    all_from_brand = available.get(brand_name, [])

    found_store = next(
        (s for s in all_from_brand if str(s['StoreId']) == str(store_id)),
        None
    )
    if not found_store:
        return jsonify({"error": f"Store with StoreId {store_id} not found in available supermarkets."}), 404

    success, reason = add_liked_store(g.list_id, brand_name, found_store)
    if not success:
        if reason == 'already_exists':
            return jsonify({"error": f"Store with StoreId {store_id} already exists in liked settings."}), 400
        return jsonify({"error": reason}), 400
    return jsonify({"message": f"Store {store_id} added to liked settings."}), 200


# ── Stats ─────────────────────────────────────────────────────────────────────

@api_bp.route('/stats', methods=['GET'])
@require_auth
@require_list
def get_stats():
    from db import get_db
    db = get_db()
    stats = db['stats'].find_one({'listId': g.list_id}, {'_id': 0, 'listId': 0})
    if not stats:
        stats = {
            "total_receipts": 0, "total_spent": 0.0, "total_items": 0,
            "average_spend_per_receipt": 0.0, "top_10_product_purchased": [],
            "top_10_price_increase": [], "top_10_price_drop": [], "receipts": {}
        }
    return jsonify(stats)


@api_bp.route('/stats/<barcode>', methods=['GET'])
@require_auth
@require_list
def get_product_stats(barcode):
    product = get_product(g.list_id, barcode)
    if product:
        return jsonify(product), 200
    return jsonify({"error": f"Product with barcode '{barcode}' not found."}), 404


# ── Favorites ─────────────────────────────────────────────────────────────────

@api_bp.route('/favorites/add', methods=['POST'])
@require_auth
@require_list
def add_product_to_favorites():
    barcode = safe_str(request.json.get('barcode', ''))
    if not barcode:
        return jsonify({"error": "Barcode is required."}), 400
    if not set_favorite(g.list_id, barcode, True):
        return jsonify({"error": f"Product with barcode '{barcode}' not found."}), 404
    return jsonify({"message": f"Product '{barcode}' added to favorites."}), 200


@api_bp.route('/favorites/remove', methods=['POST'])
@require_auth
@require_list
def remove_product_from_favorites():
    barcode = safe_str(request.json.get('barcode', ''))
    if not barcode:
        return jsonify({"error": "Barcode is required."}), 400
    if not set_favorite(g.list_id, barcode, False):
        return jsonify({"error": f"Product with barcode '{barcode}' not found."}), 404
    return jsonify({"message": f"Product '{barcode}' removed from favorites."}), 200


# ── Receipts ──────────────────────────────────────────────────────────────────

@api_bp.route('/receipts', methods=['GET'])
@require_auth
@require_list
def get_receipts_list():
    receipts = []
    try:
        for doc in get_receipts_for_list(g.list_id):
            company_name = doc.get('company', '')
            city_english = doc.get('cityEnglish', '')
            receipts.append({
                "company":     "אושר עד" if company_name == "osherad"
                               else "יוחננוף" if company_name == "yohananof"
                               else "רמי לוי" if company_name == "ramilevy"
                               else company_name,
                "city":         get_hebrew_city_name(city_english),
                "id":           doc.get('receiptId', ''),
                "file":         doc.get('receiptId', ''),
                "originalLink": doc.get('originalLink', ''),
                "total":        doc.get('total', 0),
                "createdDate":  doc.get('createdDate', 'Unknown'),
            })
    except Exception as e:
        return jsonify({"error": f"Error reading receipts: {str(e)}"}), 500
    return jsonify(receipts), 200


@api_bp.route('/receipts/<receipt_id>', methods=['GET'])
@require_auth
@require_list
def get_receipt_detail(receipt_id):
    """Return full receipt details including items for a given receiptId."""
    doc = get_receipt_by_id(g.list_id, receipt_id)
    if not doc:
        return jsonify({"error": "Receipt not found."}), 404
    company_name = doc.get('company', '')
    return jsonify({
        "id":           doc.get('receiptId', receipt_id),
        "company":      "אושר עד" if company_name == "osherad"
                        else "יוחננוף" if company_name == "yohananof"
                        else "רמי לוי" if company_name == "ramilevy"
                        else company_name,
        "city":         get_hebrew_city_name(doc.get('cityEnglish', '')),
        "total":        doc.get('total', 0),
        "createdDate":  doc.get('createdDate', ''),
        "items":        doc.get('items', []),
    }), 200


@api_bp.route('/receipts/<receipt_number>/download', methods=['GET'])
@require_auth
@require_list
def download_receipt(receipt_number):
    if not receipt_belongs_to_list(g.list_id, receipt_number):
        return jsonify({"error": "Receipt not found."}), 404
    base_path = '../original_receipts_backup'
    try:
        filename = receipt_number + '.pdf'
        if filename in os.listdir(base_path):
            receipt_path = os.path.join(base_path, filename)
            return send_file(receipt_path, as_attachment=True,
                             download_name=f'{generate_receipt_filename()}.pdf')
        return jsonify({"error": f"Receipt '{receipt_number}' not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error reading receipts directory: {str(e)}"}), 500


@api_bp.route('/receipts/<receipt_number>/show', methods=['GET'])
@require_auth
@require_list
def show_receipt(receipt_number):
    if not receipt_belongs_to_list(g.list_id, receipt_number):
        return jsonify({"error": "Receipt not found."}), 404
    base_path = '../original_receipts_backup'
    try:
        filename = receipt_number + '.pdf'
        if filename in os.listdir(base_path):
            receipt_path = os.path.join(base_path, filename)
            return send_file(receipt_path, as_attachment=False,
                             download_name=f'{generate_receipt_filename()}.pdf')
        return jsonify({"error": f"Receipt '{receipt_number}' not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error reading receipts directory: {str(e)}"}), 500


@api_bp.route('/fetchReceipt', methods=['POST'])
@limiter.limit("30 per minute")
@require_auth
@require_list
def fetch_receipt():
    list_id = g.list_id
    data    = request.get_json()
    raw_url = data.get('url')
    if not raw_url:
        return jsonify({"error": "URL is required in the request body."}), 400

    try:
        # Step 1: Follow the redirect to get the actual document URL
        redirect_response = requests.get(raw_url, allow_redirects=True)
        final_url         = redirect_response.url

        # Step 2: Parse redirected URL to extract query parameters
        parsed_url  = urlparse(final_url)
        query_params = parse_qs(parsed_url.query)
        doc_id  = query_params.get('id', [''])[0]
        p_param = query_params.get('p', [''])[0]

        if not doc_id:
            return jsonify({"error": "Could not extract document ID from redirected URL."}), 400

        # Step 3: Construct the final document fetch URL
        base_domain   = f"{parsed_url.scheme}://{parsed_url.netloc}"
        converted_url = f"{base_domain}/v1.0/documents/{doc_id}"
        if p_param:
            converted_url += f"?p={p_param}"
        print(f"Converted URL: {converted_url}")

        # Duplicate check — before we do any work
        if receipt_link_exists(list_id, raw_url):
            return jsonify({"error": "receipt already exists."}), 400

        # Step 4: Fetch the receipt data
        response = requests.get(converted_url)

        if response.status_code != 200:
            return jsonify({
                "error": f"Failed to download receipt from {converted_url}",
                "status_code": response.status_code
            }), response.status_code

        receipt_json = response.json()
        print(f"Fetched receipt data: {receipt_json}")

        company_name = ""
        if 'osher' in final_url:
            company_name = "osherad"
        elif 'yohananof' in final_url:
            company_name = "yohananof"
        elif 'rami-levy' in final_url:
            company_name = "ramilevy"

        try:
            filename_value = receipt_json['additionalInfo'][0]['value'].replace("@", "")
            print(f"Extracted filename value: {filename_value}")
        except (KeyError, TypeError):
            return jsonify({"error": "Could not find 'additionalInfo.value' in receipt data."}), 500

        city_english = "Unknown City"
        try:
            city_hebrew  = receipt_json['store']['name']
            print(f"Branch identified: {city_hebrew}")
            import json as _json
            with open('../databases/cities.json', 'r', encoding='utf-8') as f:
                city_translation_map = _json.load(f)
            city_english = city_translation_map.get(city_hebrew, "Unknown City")
            print(f"Hebrew city '{city_hebrew}' → '{city_english}'.")
        except KeyError:
            print("Branch name not found in receipt data.")

        # Step 5: Download original PDF backup (file system — unchanged)
        try:
            original_receipt_path = f"https://pdf.pairzon.com/pdf/{doc_id}/{p_param}"
            print(f"Downloading original receipt for backup: {original_receipt_path}")
            original_receipt_response = requests.get(original_receipt_path)
            if original_receipt_response.status_code == 200:
                original_receipt_save_path = f"../original_receipts_backup/{filename_value}.pdf"
                os.makedirs(os.path.dirname(original_receipt_save_path), exist_ok=True)
                with open(original_receipt_save_path, 'wb') as f:
                    f.write(original_receipt_response.content)
                print(f"Original receipt saved to {original_receipt_save_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading original receipt: {str(e)}")
            return jsonify({"error": f"Failed to download original receipt: {str(e)}"}), 500

        # Step 6: Save receipt metadata to MongoDB + process products/stats
        created_date = receipt_json.get('createdDate', '').replace("T", " ")
        total        = receipt_json.get('total', 0.0)

        raw_items = receipt_json.get('items', [])
        normalized_items = [
            {
                'code':     str(it.get('code', '')),
                'name':     it.get('name', ''),
                'price':    float(it.get('price', 0)),
                'quantity': int(it.get('quantity', 1)),
                'total':    float(it.get('total', 0)),
            }
            for it in raw_items
            if it.get('code') != '901046' and it.get('name') != 'מיחזור אריזה'
        ]

        save_receipt(
            list_id      = list_id,
            original_link = raw_url,
            company       = company_name,
            city_english  = city_english,
            receipt_id    = filename_value,
            total         = total,
            created_date  = created_date,
            items         = normalized_items,
        )

        process_receipt_mongo(list_id, receipt_json, original_link=raw_url, company=company_name)

        return jsonify({
            "message":       "Receipt fetched and processed successfully.",
            "converted_url": converted_url,
            "saved_filename": filename_value,
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error during receipt fetch: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error processing receipt: {str(e)}", "stacktrace": traceback.format_exc()}), 500


@api_bp.route('/receipts/check-links', methods=['POST'])
@limiter.limit("20 per minute")
@require_auth
@require_list
def check_receipt_links():
    """
    Batch duplicate check before SMS sync.
    Body:    { "urls": ["url1", "url2", ...] }
    Returns: { "existing": [...], "new": [...] }
    """
    data = request.get_json()
    urls = data.get('urls', [])
    if not isinstance(urls, list):
        return jsonify({"error": "urls must be a list."}), 400

    list_id  = g.list_id
    existing = [u for u in urls if receipt_link_exists(list_id, u)]
    new_urls = [u for u in urls if not receipt_link_exists(list_id, u)]

    return jsonify({"existing": existing, "new": new_urls}), 200


@api_bp.route('/receipts/sync', methods=['POST'])
@limiter.limit("25 per minute")
@require_auth
@require_list
def sync_receipt():
    """
    SMS-sync endpoint — supports Pairzon (Osher Ad) and wee.ai (Yochananof) URLs.

    - Duplicate link → HTTP 200 {"status": "duplicate"} (non-error, client skips silently)
    - PDF/backup failure is non-fatal
    - Body: { "url": "<receipt URL from SMS>" }
    """
    list_id = g.list_id
    data    = request.get_json()
    raw_url = data.get('url')
    if not raw_url:
        return jsonify({"error": "URL is required."}), 400

    # ── Duplicate prevention ──────────────────────────────────────────────────
    if receipt_link_exists(list_id, raw_url):
        return jsonify({"status": "duplicate"}), 200

    try:
        import json as _json

        # ── Branch: wee.ai (Yochananof) ───────────────────────────────────────
        if 'wee.ai' in raw_url:
            # Step 1: follow the redirect to extract the receipt UUID (q param)
            print(f"[wee.ai] fetching redirect for: {raw_url}")
            redirect_resp  = requests.get(raw_url, allow_redirects=True, timeout=15)
            redirected_url = redirect_resp.url
            print(f"[wee.ai] redirected to: {redirected_url}")

            redirect_qs  = parse_qs(urlparse(redirected_url).query)
            receipt_uuid = redirect_qs.get('q', [''])[0]
            print(f"[wee.ai] receipt_uuid: {receipt_uuid!r}")

            if not receipt_uuid:
                print(f"[wee.ai] ERROR: no q param in redirect URL: {redirected_url}")
                return jsonify({"error": f"Could not extract receipt UUID from wee.ai redirect. Final URL: {redirected_url}"}), 400

            # Step 2: fetch real receipt JSON using the UUID
            api_url  = f"https://wee.ai/api/receipts/{receipt_uuid}"
            print(f"[wee.ai] fetching receipt API: {api_url}")
            wee_resp = requests.get(api_url, timeout=15)
            print(f"[wee.ai] API status: {wee_resp.status_code}")
            if wee_resp.status_code != 200:
                print(f"[wee.ai] API body: {wee_resp.text[:500]}")
                return jsonify({"error": f"Failed to fetch wee.ai receipt (HTTP {wee_resp.status_code})"}), 502

            wee_list = wee_resp.json()
            if not wee_list:
                return jsonify({"error": "Empty response from wee.ai"}), 502

            w = wee_list[0]
            print(f"[wee.ai] receipt id={w.get('id')} total={w.get('total')} createdDate={w.get('createdDate')} items={len(w.get('items', []))}")

            # Step 3: save raw JSON backup — non-fatal
            try:
                backup_id   = str(w.get('id', receipt_uuid))
                backup_path = f"../original_receipts_backup/yochananof_{backup_id}.json"
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                with open(backup_path, 'w', encoding='utf-8') as f:
                    _json.dump(w, f, ensure_ascii=False, indent=2)
                print(f"[wee.ai] JSON backup saved: {backup_path}")
            except Exception as backup_err:
                print(f"[wee.ai] JSON backup failed (non-fatal): {backup_err}")

            # Normalise to the same structure that process_receipt_mongo expects.
            # Items: wee.ai uses itemCode (not code); total is the line total.
            receipt_json = {
                'createdDate':   (w.get('createdDate') or ''),
                'total':         w.get('total', 0.0),
                'barcode':       w.get('barcode') or w.get('transactionNumber', receipt_uuid),
                'numberOfItems': len(w.get('items', [])),
                'items': [
                    {
                        'code':     item.get('itemCode', ''),
                        'name':     item.get('name', ''),
                        'price':    item.get('price', 0),
                        'quantity': item.get('quantity', 1),
                        'total':    item.get('total') or (item.get('price', 0) * item.get('quantity', 1)),
                    }
                    for item in w.get('items', [])
                ],
            }

            company_name   = "yohananof"
            filename_value = str(w.get('id', receipt_uuid))

            # tBranch.branchName is already in Hebrew — store it directly.
            # get_hebrew_city_name() returns unknown values as-is, so display works.
            city_english = (w.get('tBranch') or {}).get('branchName') or 'Unknown City'

            created_date = receipt_json['createdDate'].replace("T", " ")
            total        = float(receipt_json.get('total', 0.0))
            print(f"[wee.ai] parsed — city={city_english!r} created={created_date!r} total={total}")

        # ── Branch: Pairzon (Osher Ad) ────────────────────────────────────────
        else:
            redirect_response = requests.get(raw_url, allow_redirects=True, timeout=15)
            final_url         = redirect_response.url

            parsed_url   = urlparse(final_url)
            query_params = parse_qs(parsed_url.query)
            doc_id  = query_params.get('id', [''])[0]
            p_param = query_params.get('p', [''])[0]

            if not doc_id:
                return jsonify({"error": "Could not extract document ID from redirected URL."}), 400

            base_domain   = f"{parsed_url.scheme}://{parsed_url.netloc}"
            converted_url = f"{base_domain}/v1.0/documents/{doc_id}"
            if p_param:
                converted_url += f"?p={p_param}"

            response = requests.get(converted_url, timeout=15)
            if response.status_code != 200:
                return jsonify({"error": f"Failed to fetch receipt (HTTP {response.status_code})"}), 502

            receipt_json = response.json()

            if 'osher' in final_url:
                company_name = "osherad"
            elif 'rami-levy' in final_url:
                company_name = "ramilevy"
            elif 'yohananof' in final_url:
                company_name = "yohananof"
            else:
                company_name = ""

            try:
                filename_value = receipt_json['additionalInfo'][0]['value'].replace("@", "")
            except (KeyError, TypeError):
                return jsonify({"error": "Could not parse additionalInfo from receipt."}), 500

            city_english = "Unknown City"
            try:
                city_hebrew = receipt_json['store']['name']
                with open('../databases/cities.json', 'r', encoding='utf-8') as f:
                    city_map = _json.load(f)
                city_english = city_map.get(city_hebrew, "Unknown City")
            except Exception:
                pass

            # PDF backup — non-fatal
            try:
                pdf_url  = f"https://pdf.pairzon.com/pdf/{doc_id}/{p_param}"
                pdf_resp = requests.get(pdf_url, timeout=15)
                if pdf_resp.status_code == 200:
                    save_path = f"../original_receipts_backup/{filename_value}.pdf"
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, 'wb') as f:
                        f.write(pdf_resp.content)
            except Exception as pdf_err:
                print(f"sync_receipt: PDF backup failed (non-fatal): {pdf_err}")

            created_date = receipt_json.get('createdDate', '').replace("T", " ")
            total        = receipt_json.get('total', 0.0)

        # ── Common: persist ───────────────────────────────────────────────────
        # process first — if it fails the receipt is NOT marked as seen so the
        # client can retry the same URL on the next sync.
        raw_items = receipt_json.get('items', [])
        normalized_items = [
            {
                'code':     str(it.get('code', '')),
                'name':     it.get('name', ''),
                'price':    float(it.get('price', 0)),
                'quantity': int(it.get('quantity', 1)),
                'total':    float(it.get('total', 0)),
            }
            for it in raw_items
            if it.get('code') != '901046' and it.get('name') != 'מיחזור אריזה'
        ]

        process_receipt_mongo(list_id, receipt_json, original_link=raw_url, company=company_name)
        save_receipt(
            list_id       = list_id,
            original_link = raw_url,
            company       = company_name,
            city_english  = city_english,
            receipt_id    = filename_value,
            total         = total,
            created_date  = created_date,
            items         = normalized_items,
        )

        return jsonify({"status": "processed", "saved_filename": filename_value}), 200

    except requests.exceptions.Timeout:
        print(f"[sync_receipt] Timeout for URL: {raw_url}")
        return jsonify({"error": "Request timed out."}), 504
    except requests.exceptions.RequestException as e:
        print(f"[sync_receipt] Network error for URL: {raw_url} — {e}")
        return jsonify({"error": f"Network error: {str(e)}"}), 500
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[sync_receipt] Unexpected error for URL: {raw_url}\n{tb}")
        return jsonify({"error": f"Unexpected error: {str(e)}", "stacktrace": tb}), 500


@api_bp.route('/receipts/scan-manual', methods=['POST'])
@limiter.limit("20 per minute")
@require_auth
@require_list
def scan_manual_receipt():
    """
    Save a manually camera-scanned receipt.

    Body:
        receiptNumber  str   — receipt ID printed on the physical receipt (required)
        receiptType    str   — "חשבונית מס/קבלה" | "חשבונית קבלה"
        items          list  — [{ barcode, name, quantity }]
        date           str   — "DD/MM/YYYY"
        time           str   — "HH:MM"
        total          float — final total
        company        str   — "osherad" | "yohananof" | "ramilevy" | "shufersal" | ...
        city           str   — optional city name

    Returns 409 {"status": "duplicate"} if this receiptNumber was already manually scanned.
    """
    from datetime import datetime as _dt

    list_id = g.list_id
    data    = request.get_json()

    receipt_number = safe_str(data.get('receiptNumber', ''))
    receipt_type   = safe_str(data.get('receiptType', 'חשבונית מס/קבלה'))
    items_raw      = data.get('items') or []
    date_str       = safe_str(data.get('date', ''))
    time_str       = safe_str(data.get('time', ''))
    total          = float(data.get('total') or 0.0)
    company        = safe_str(data.get('company', ''))
    city           = safe_str(data.get('city', ''))

    if not receipt_number:
        return jsonify({'error': 'receiptNumber is required.'}), 400

    # Duplicate prevention — only among manually scanned receipts
    if manual_receipt_number_exists(list_id, receipt_number):
        return jsonify({'status': 'duplicate'}), 409

    # Parse date DD/MM/YYYY → YYYY-MM-DD HH:MM:00
    created_date = date_str
    try:
        parsed = _dt.strptime(date_str, '%d/%m/%Y')
        created_date = f"{parsed.strftime('%Y-%m-%d')} {time_str}:00" if time_str else parsed.strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        if time_str:
            created_date = f"{date_str} {time_str}:00"

    normalized_items = [
        {
            'code':     safe_str(it.get('barcode', '')),
            'name':     safe_str(it.get('name', '')),
            'price':    0.0,
            'quantity': int(it.get('quantity') or 1),
            'total':    0.0,
        }
        for it in items_raw
        if it.get('barcode')
    ]

    pseudo_link = f"manual://{receipt_number}"

    save_receipt(
        list_id          = list_id,
        original_link    = pseudo_link,
        company          = company,
        city_english     = city,
        receipt_id       = receipt_number,
        total            = total,
        created_date     = created_date,
        items            = normalized_items,
        scanned_manually = True,
        receipt_type     = receipt_type,
    )

    # Update global stats (total_receipts, total_spent) — pass empty items
    # to avoid corrupting product price stats where we have no price data.
    process_receipt_mongo(
        list_id,
        {
            'createdDate':   created_date,
            'total':         total,
            'barcode':       receipt_number,
            'numberOfItems': len(normalized_items),
            'items':         [],
        },
        original_link=pseudo_link,
        company=company,
    )

    return jsonify({'status': 'ok', 'receiptId': receipt_number}), 200


# ── Products ──────────────────────────────────────────────────────────────────

@api_bp.route('/products', methods=['GET'])
@require_auth
@require_list
def get_products():
    offset = safe_int(request.args.get('offset', 0), default=0)
    limit  = min(safe_int(request.args.get('limit', 30), default=30), 100)
    query  = safe_str(request.args.get('q', ''))
    return jsonify(get_products_paged(g.list_id, offset, limit, query))


@api_bp.route('/productsbrowser', methods=['GET'])
@require_auth
@require_list
def get_productsBrowser():
    return jsonify(get_products_dict(g.list_id))


@api_bp.route('/regular-basket', methods=['GET'])
@require_auth
@require_list
def get_regular_basket_route():
    """Return the user's regular basket — top 30% of products by total quantity purchased."""
    return jsonify(get_regular_basket(g.list_id))


@api_bp.route('/product/<barcode>/settings', methods=['GET'])
@require_auth
@require_list
def get_product_settings(barcode):
    barcode = request.view_args.get('barcode')
    if not barcode:
        return jsonify({"error": "Barcode is required."}), 400
    product = get_product(g.list_id, barcode)
    if not product:
        return jsonify({"error": f"Product with barcode '{barcode}' not found."}), 404
    settings = product.get('settings', {})
    settings['barcode'] = product['barcode']
    settings['name']    = product['name']
    return jsonify(settings), 200


# ── Prices ────────────────────────────────────────────────────────────────────

@api_bp.route('/prices', methods=['GET'])
@require_auth
@require_list
def get_prices():
    all_prices_data = []
    try:
        liked = get_liked(g.list_id)
        parsed_prices_folder = '../databases/liked_supermarkets_parsed_prices'

        for supermarket_name, branches in liked.items():
            for branch in branches:
                branch_id = branch.get('StoreId')
                filename  = f"{supermarket_name}_{branch_id}_full_prices.json"
                file_path = os.path.join(parsed_prices_folder, filename)

                if os.path.exists(file_path):
                    import json as _json
                    with open(file_path, 'r', encoding='utf-8') as price_file:
                        price_data = _json.load(price_file)
                        price_data[supermarket_name] = branch
                        all_prices_data.append(price_data)
                else:
                    print(f"File not found: {file_path}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(all_prices_data)
