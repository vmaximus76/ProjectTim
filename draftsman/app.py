from flask import Flask, request, jsonify
import os
import logging
from .translator import IntentParser

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional API‑key protection – if env var API_KEY is set, require header
API_KEY = os.getenv('API_KEY')

@app.before_request
def require_api_key():
    if API_KEY:
        header = request.headers.get('X-API-KEY')
        if header != API_KEY:
            return jsonify({"error": "unauthorized"}), 401

parser = IntentParser()

@app.route('/draft', methods=['POST'])
def draft():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    data = request.get_json()
    intent = data.get('intent')
    if not intent:
        return jsonify({"error": "Missing 'intent' field"}), 400
    try:
        tim_ir = parser.translate(intent)
        return jsonify({"tim_ir": tim_ir}), 200
    except Exception as e:
        logger.exception('Translation error')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Development server – runs on 8081 to avoid conflict with Governor
    app.run(host='0.0.0.0', port=8081, debug=False)