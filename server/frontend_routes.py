# frontend_routes.py
from flask import Blueprint, redirect, url_for, render_template


frontend_bp = Blueprint('frontend', __name__, url_prefix='/')

@frontend_bp.route('/')
def home_page():
    return redirect(url_for('frontend.shopping_list_page'))


@frontend_bp.route('/list', methods=['GET'])
def shopping_list_page():
    return render_template('list.html')


@frontend_bp.route('/generalSettings', methods=['GET'])
def general_settings_page():
    return render_template('general_settings.html')


@frontend_bp.route('/productsBrowser', methods=['GET'])
def productsBrowser_page():
    return render_template('productsBrowser.html')

@frontend_bp.route('/stats', methods=['GET'])
def overall_stats_page():
    return render_template('stats.html')


@frontend_bp.route('/stats/<product_barcode>', methods=['GET'])
def specific_product_stats_page(product_barcode):
    return render_template('product_stats.html', barcode=product_barcode)


@frontend_bp.route('/receipts', methods=['GET'])
def receipts_list_page():
    return render_template('receipts.html')


@frontend_bp.route('/receipts/<transaction_id>', methods=['GET'])
def display_receipt_page(receipt_name):
    return render_template('receipt_detail.html', receipt_name=receipt_name)


@frontend_bp.route('/products', methods=['GET'])
def products_list_page():
    return render_template('products.html')


@frontend_bp.route('/product/<product_barcode>/settings', methods=['GET'])
def product_settings_page(product_barcode):
    if product_barcode:
        return render_template('settings.html', barcode=product_barcode)
    return "<h1>Product Settings</h1><p>Please specify a product barcode to view/edit its settings. (Frontend)</p>"
