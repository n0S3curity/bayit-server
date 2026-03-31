# main.py
import threading
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from api_routes import api_bp
from frontend_routes import frontend_bp
from list_routes import list_bp
from helpers import *
from supermarkets_scrapper import Scrapper
from db import init_indexes
from extensions import limiter


def main():
    app = Flask(__name__)

    # Trust one layer of reverse-proxy headers so rate limiting uses the
    # real client IP rather than the proxy's address.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["Authorization", "Content-Type"])

    # Attach Flask-Limiter to the app
    limiter.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(list_bp)
    app.register_blueprint(frontend_bp)
    # create db files if they do not exist
    create_db_files()
    # Initialize MongoDB indexes
    init_indexes()
    # Initialize the scraper
    scraper = Scrapper()
    # Start the scraper in a separate thread
    # osherad_scraper_thread = threading.Thread(target=scraper.run_scraper_for_osher_ad, daemon=True)
    # osherad_scraper_thread.start()
    # yohananof_scraper_thread = threading.Thread(target=scraper.run_scraper_for_yohananof, daemon=True)
    # yohananof_scraper_thread.start()

    # listen on all ips
    app.run(host='0.0.0.0', debug=True, port=5000)


if __name__ == '__main__':
    main()