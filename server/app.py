# main.py
import threading
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS  # New import for CORS

from api_routes import api_bp  # Import your blueprint
from frontend_routes import frontend_bp  # Import your frontend blueprint
from helpers import *
from supermarkets_scrapper import Scrapper  # Import the scraper module


def main():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["Authorization", "Content-Type"])  # Enable CORS for all routes

    # Register the Blueprint
    # All routes defined in api_bp will now be accessible under the /api prefix
    app.register_blueprint(api_bp)
    app.register_blueprint(frontend_bp)
    # create db files if they do not exist
    create_db_files()
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