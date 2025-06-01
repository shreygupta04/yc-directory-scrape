from flask import Flask, request, render_template, jsonify
from scrape_runner import run_scrape
from scripts.progress import get_progress
from threading import Thread

app = Flask(__name__, template_folder="../templates")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_scrape():
    batch = request.form["batch"]

    def async_scrape():
        run_scrape(batch)

    Thread(target=async_scrape).start()
    return jsonify({"status": "started"})

@app.route("/progress", methods=["GET"])
def progress():
    return jsonify(get_progress())

if __name__ == "__main__":
    app.run(debug=True, port=5000)