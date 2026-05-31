from flask import Flask, request, jsonify
import json
import jsonschema
import logging
import hashlib
import time
from inspector.engine import verify_tim_ir
from registry.db import init_db, get_adu_value
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional API‑key protection – if the env var API_KEY is set, callers must provide it
API_KEY = os.getenv('API_KEY')

@app.before_request
def require_api_key():
    if API_KEY:
        header = request.headers.get('X-API-KEY')
        if header != API_KEY:
            return jsonify({"error": "unauthorized"}), 401

# Load TIM-IR schema
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'tim_ir_schema.json')
with open(SCHEMA_PATH, 'r') as f:
    TIM_IR_SCHEMA = json.load(f)

# Initialize registry DB (singleton)
DB_PATH = os.getenv('TIM_REGISTRY_DB', os.path.join(os.path.dirname(__file__), '..', 'registry', 'tim_registry.db'))
init_db(DB_PATH)

def compute_hash(data: dict) -> str:
    """Compute SHA256 hash of deterministic JSON representation."""
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

@app.route('/verify', methods=['POST'])
def verify():
    start_time = time.time()
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    try:
        payload = request.get_json()
        # Validate against TIM-IR schema
        jsonschema.validate(instance=payload, schema=TIM_IR_SCHEMA)
    except jsonschema.exceptions.ValidationError as ve:
        logger.warning(f"Schema validation failed: {ve.message}")
        return jsonify({"error": f"Invalid TIM-IR: {ve.message}"}), 400
    except Exception as e:
        logger.error(f"JSON parsing error: {e}")
        return jsonify({"error": "Malformed JSON"}), 400

    # Compute hash for audit log
    payload_hash = compute_hash(payload)

    try:
        result = verify_tim_ir(payload)
        # Attach metadata
        result['payload_hash'] = payload_hash
        result['processing_time_ms'] = int((time.time() - start_time) * 1000)
        logger.info(f"Verification completed: status={result.get('status')} hash={payload_hash}")
        return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Verification error: {e}")
        return jsonify({
            "error": "Internal verification error",
            "payload_hash": payload_hash
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)