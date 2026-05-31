import pytest
from inspector.engine import verify_tim_ir

def test_simple_constant_verification():
    # 5 == 5 should be SAT (VERIFIED)
    ir = {"type": "eq", "left": {"type": "const", "value": 5}, "right": {"type": "const", "value": 5}}
    result = verify_tim_ir(ir)
    assert result["status"] == "VERIFIED"

def test_unsat_comparison():
    # 3 > 10 is UNSAT (VERIFICATION_FAILED)
    ir = {"type": "gt", "left": {"type": "const", "value": 3}, "right": {"type": "const", "value": 10}}
    result = verify_tim_ir(ir)
    assert result["status"] == "VERIFICATION_FAILED"
