from enum import Enum

class TIMOperation(str, Enum):
    CONST = 'const'
    VAR = 'var'
    LOOKUP = 'lookup'
    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    DIV = 'div'
    EQ = 'eq'
    LT = 'lt'
    GT = 'gt'
    AND = 'and'
    OR = 'or'
    NOT = 'not'

class TIMIRNode:
    def __init__(self, type: TIMOperation, **kwargs):
        self.type = type
        self._data = kwargs

    def to_dict(self):
        return {
            'type': self.type.value,
            **{k: v for k, v in self._data.items() if k != '_data'}
        }

    @classmethod
    def from_dict(cls, data):
        type_enum = None
        for op in TIMOperation:
            if op.value == data['type']:
                type_enum = op
                break
        if not type_enum:
            raise ValueError(f"Unknown TIM-IR node type: {data['type']}")
        return cls(type_enum, **data)

# Example parser functions

def parse_constant(value: str or int) -> TIMIRNode:
    return TIMIRNode(TIMOperation.CONST, value=value)


def parse_variable(name: str) -> TIMIRNode:
    return TIMIRNode(TIMOperation.VAR, name=name)


def parse_lookup(name: str) -> TIMIRNode:
    return TIMIRNode(TIMOperation.LOOKUP, name=name)


def parse_binary_op(op_type: TIMOperation, left: TIMIRNode, right: TIMIRNode) -> TIMIRNode:
    if op_type in {TIMOperation.ADD, TIMOperation.SUB, TIMOperation.MUL, TIMOperation.DIV}:
        return TIMIRNode(op_type, args=[left.to_dict(), right.to_dict()])
    return TIMIRNode(op_type, left=left.to_dict(), right=right.to_dict())