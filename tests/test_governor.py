import json
import pytest
from governor.app import app as governor_app
from registry.db import init_db, add_adu, DEFAULT_DB_PATH

@pytest.fixture(autouse=True)
def setup_registry(tmp_path):
    # Use a temporary DB for tests
    db_path = tmp_path / 'test_registry.db'
    init_db(db_path)
    # Monkey‑patch the DEFAULT_DB_PATH used by the module
    from registry import db as reg_mod
    reg_mod.DEFAULT_DB_PATH = db_path
    # Seed a few ADUs
    add_adu('MAX_TEMP', 100)
    add_adu('MIN_TEMP', 0)
    yield

def test_verify_simple_eq():
    client = governor_app.test_client()
    payload = {
        "type": "eq",
        "left": {"type": "const", "value": 5},
        "right": {"type": "const", "value": 5}
    }
    resp = client.post('/verify', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'VERIFIED'

def test_verify_lookup_success():
    client = governor_app.test_client()
    payload = {
        "type": "eq",
        "left": {"type": "lookup", "name": "MAX_TEMP"},
        "right": {"type": "const", "value": 100}
    }
    resp = client.post('/verify', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'VERIFIED'

def test_verify_invalid_schema():
    client = governor_app.test_client()
    # Missing required "type" field
    payload = {"invalid": "data"}
    resp = client.post('/verify', json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data
