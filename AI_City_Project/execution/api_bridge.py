from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from db_engine import DBEngine

app = Flask(__name__)
CORS(app)
db = DBEngine()

# --- Configurations ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
OPS_DIR = os.path.join(PROJECT_ROOT, 'ops')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

@app.route('/')
def index():
    """Serves the main dashboard."""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    """Serves other frontend assets."""
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns general system status."""
    try:
        import psutil
        health = {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "status": "Operational"
        }
    except:
        health = {"status": "Unknown"}
    return jsonify(health)

@app.route('/api/citizens', methods=['GET'])
def get_citizens():
    """Returns all citizens from DB."""
    citizens = db.get_all_citizens()
    return jsonify(citizens)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Returns latest system logs."""
    log_file = os.path.join(OPS_DIR, 'system_log.md')
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return jsonify(lines[-20:]) # Last 20 logs
    return jsonify([])

@app.route('/api/niches', methods=['GET'])
def get_niche():
    """Returns latest discovered niche."""
    niche_file = os.path.join(OPS_DIR, 'latest_niche.json')
    if os.path.exists(niche_file):
        with open(niche_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({"niche": "None"})

@app.route('/api/ascend', methods=['POST'])
def trigger_ascension():
    """Trigger the cloud migration sequence."""
    # In a real scenario, this would push to git
    # For now, we return the One-Click Render Link
    deployment_url = "https://render.com/deploy?repo=https://github.com/aicity-sovereign/OS"
    return jsonify({
        "status": "Initiated",
        "url": deployment_url,
        "message": "소장님, 준비가 끝났습니다. 아래 버튼을 눌러 승천을 완료하십시오."
    })

if __name__ == '__main__':
    # Start on custom port to avoid conflicts
    app.run(host='0.0.0.0', port=5000, debug=False)
