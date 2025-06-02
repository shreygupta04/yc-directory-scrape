import sys
import os
from flask import Flask, request, render_template, jsonify
from threading import Thread
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after adding to path
from scrape_runner import run_scrape
from scripts.progress import get_progress, reset_progress

app = Flask(__name__, template_folder="templates")

# Global flag to track if scraping is running
scraping_active = False

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_scrape():
    global scraping_active
    
    if scraping_active:
        return jsonify({"status": "error", "message": "Scraping already in progress"}), 400
    
    batch = request.form.get("batch")
    if not batch:
        return jsonify({"status": "error", "message": "Batch parameter required"}), 400

    print(f"Starting scrape for batch: {batch}")
    
    def async_scrape():
        global scraping_active
        try:
            scraping_active = True
            reset_progress()  # Reset progress before starting
            run_scrape(batch)
        except Exception as e:
            print(f"Error in async_scrape: {e}")
            traceback.print_exc()
        finally:
            scraping_active = False
            print("Scraping thread completed")

    # Start the scraping in a separate thread
    thread = Thread(target=async_scrape)
    thread.daemon = True  # Make thread daemon so it doesn't prevent app shutdown
    thread.start()
    
    return jsonify({"status": "started"})

@app.route("/progress", methods=["GET"])
def progress():
    progress_data = get_progress()
    print(f"Progress requested: {progress_data}")  # Debug logging
    return jsonify(progress_data)

@app.route("/status", methods=["GET"])
def status():
    """Additional endpoint to check if scraping is active"""
    return jsonify({"scraping_active": scraping_active})

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True, port=5000, threaded=True)