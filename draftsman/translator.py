import re
from typing import Dict, Any
from .model import TIMIRNode, TIMOperation, parse_constant, parse_variable, parse_lookup, parse_binary_op

class IntentParser:
    """
    Simple rule-based translator from natural language to TIM-IR.
    Supports patterns like:
    - "x plus 5" -> add(var('x'), const(5))
    - "temperature greater than 100" -> gt(lookup('temperature'), const(100))
    """

    BINARY_PATTERNS = [
        (r'(\w+)\s*\+ (\d+)', TIMOperation.ADD),
        (r'(\w+)\s*-\s*(\d+)', TIMOperation.SUB),
        (r'(\w+)\s*\* (\d+)', TIMOperation.MUL),
        (r'(\w+)\s*/\s*(\d+)', TIMOperation.DIV),
        (r'(\w+)\s*>\s*(\d+)', TIMOperation.GT),
        (r'(\w+)\s*<\s*(\d+)', TIMOperation.LT),
        (r'(\w+)\s*>=\s*(\d+)', TIMOperation.GT),  # Simplified
        (r'(\w+)\s*<=\s*(\d+)', TIMOperation.LT),  # Simplified
    ]

    UNARY_PATTERNS = [
        (r'not\s+(\w+)', TIMOperation.NOT),
    ]

    def __init__(self):
        self._adu_names: Dict[str, str] = {}

    def register_adu(self, name: str, description: str):
        """Register a known ADU for lookup resolution"""
        self._adu_names[description.lower()] = name

    def translate(self, intent: str) -> Dict[str, Any]:
        """Translate natural language intent to TIM-IR"""
        intent = intent.strip().lower()

        # Handle binary operations
        for pattern, op in self.BINARY_PATTERNS:
            match = re.search(pattern, intent)
            if match:
                left = parse_variable(match.group(1)) if match.group(1).isalpha() else parse_lookup(match.group(1))
                right = parse_constant(int(match.group(2)))
                return parse_binary_op(op, left, right).to_dict()

        # Handle simple lookups
        lookup_patterns = [
            (r'(\w+)\s*(?:is|greater than|less than|equals?)\s*(\d+)', TIMOperation.GT),
            (r'(\w+)\s*(?:is|greater than|less than|equals?)\s*(\d+)', TIMOperation.LT),
        ]

        # Default: return a variable node
        words = intent.split()
        if words:
            return parse_variable(words[0]).to_dict()

        raise ValueError(f"Cannot parse intent: {intent}")