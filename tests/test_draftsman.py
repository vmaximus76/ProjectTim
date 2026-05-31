import pytest
from draftsman.translator import IntentParser

@pytest.fixture
def parser():
    return IntentParser()

def test_simple_addition(parser):
    # "x + 5" should translate to an add node with var and const
    ir = parser.translate('x + 5')
    assert ir["type"] == "add"
    assert ir["args"][0]["type"] == "var"
    assert ir["args"][0]["name"] == "x"
    assert ir["args"][1]["type"] == "const"
    assert ir["args"][1]["value"] == 5

def test_greater_than(parser):
    # "temp > 100" -> gt node
    ir = parser.translate('temp > 100')
    assert ir["type"] == "gt"
    assert ir["left"]["type"] == "var"
    assert ir["right"]["type"] == "const"
    assert ir["right"]["value"] == 100
