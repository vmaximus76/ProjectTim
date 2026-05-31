"""Inspector engine – translates TIM‑IR to Z3 and runs verification.

The implementation is deliberately simple and supports a core subset of
operations required for the proof‑of‑concept:

- ``const`` – numeric constant
- ``var``   – symbolic variable (prefixed with ``var_``)
- ``lookup`` – fetch a numeric value from the immutable Axiomatic Registry
- binary arithmetic: ``add``, ``sub``, ``mul``, ``div``
- comparison: ``eq``, ``lt``, ``gt``
- Boolean combinators: ``and``, ``or``, ``not``

The ``translate_node`` function walks the TIM‑IR tree recursively and
produces a Z3 expression.  ``verify_tim_ir`` then asks Z3 whether the
expression is satisfiable and returns a deterministic JSON payload.
"""

import z3
from typing import Any, Dict
from registry.db import get_adu_value


def _translate(node: Dict[str, Any]) -> z3.ArithRef:
    """Recursively translate a TIM‑IR node into a Z3 arithmetic expression.

    Supported node shapes (minimal subset)::
        {"type": "const", "value": 5}
        {"type": "var",   "name": "x"}
        {"type": "lookup", "name": "ADU_foo"}
        {"type": "add", "args": [node1, node2]}
        {"type": "sub", "args": [node1, node2]}
        {"type": "mul", "args": [node1, node2]}
        {"type": "div", "args": [node1, node2]}
        {"type": "eq",  "left": node1, "right": node2}
        {"type": "lt",  "left": node1, "right": node2}
        {"type": "gt",  "left": node1, "right": node2}
        {"type": "and", "args": [bool1, bool2]}
        {"type": "or",  "args": [bool1, bool2]}
        {"type": "not", "arg": bool}
    """
    node_type = node["type"]

    if node_type == "const":
        return z3.IntVal(int(node["value"]))
    if node_type == "var":
        # Symbolic variable – prefixed to avoid clashes with potential ADU names
        return z3.Int(f"var_{node["name"]}")
    if node_type == "lookup":
        # Resolve ADU value from the immutable registry (must be numeric)
        adu_name = node["name"]
        val = get_adu_value(adu_name)
        return z3.IntVal(int(val))

    # Binary arithmetic helpers
    if node_type in {"add", "sub", "mul", "div"}:
        args = [_translate(arg) for arg in node["args"]]
        if node_type == "add":
            return z3.Sum(*args)
        if node_type == "sub":
            # Z3 does not have a direct Sub, use a - b - c ... chain
            result = args[0]
            for a in args[1:]:
                result = result - a
            return result
        if node_type == "mul":
            result = args[0]
            for a in args[1:]:
                result = result * a
            return result
        if node_type == "div":
            result = args[0]
            for a in args[1:]:
                result = result / a
            return result

    # Comparison operators – produce BoolRef
    if node_type in {"eq", "lt", "gt"}:
        left = _translate(node["left"])
        right = _translate(node["right"])
        if node_type == "eq":
            return left == right
        if node_type == "lt":
            return left < right
        if node_type == "gt":
            return left > right

    # Boolean combinators
    if node_type == "and":
        args = [_translate(arg) for arg in node["args"]]
        return z3.And(*args)
    if node_type == "or":
        args = [_translate(arg) for arg in node["args"]]
        return z3.Or(*args)
    if node_type == "not":
        arg = _translate(node["arg"])
        return z3.Not(arg)

    raise ValueError(f"Unsupported TIM‑IR node type: {node_type}")


def verify_tim_ir(tim_ir: Dict[str, Any]) -> Dict[str, Any]:
    """Run deterministic verification of a TIM‑IR payload.

    Returns a JSON‑serialisable dict with at least a ``status`` field:
        - ``VERIFIED``               – Z3 reports ``sat``
        - ``VERIFICATION_FAILED``    – Z3 reports ``unsat``
        - ``NULL_TRUTH``             – Z3 reports ``unknown``
    Optional ``proof`` and ``error`` fields are added for debugging.
    """
    try:
        expr = _translate(tim_ir)
        solver = z3.Solver()
        solver.add(expr)
        result = solver.check()
        if result == z3.sat:
            return {"status": "VERIFIED", "proof": "z3_sat"}
        if result == z3.unsat:
            return {"status": "VERIFICATION_FAILED"}
        return {"status": "NULL_TRUTH"}
    except Exception as exc:
        # Any translation or solver exception maps to a verification failure
        return {"status": "VERIFICATION_FAILED", "error": str(exc)}