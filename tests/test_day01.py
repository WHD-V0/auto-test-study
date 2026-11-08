import pytest
from src.calculator import Calculator

def test_add():
    calc = Calculator()
    actual = calc.add(1, 2)
    assert actual == 3

def test_negative_add():
    calc = Calculator()
    actual = calc.add(-1, -2)
    assert actual == -3

def test_add_zero():
    calc = Calculator()
    actual = calc.add(6, 0)
    assert actual == 6

def test_divide_by_zero():
    with pytest.raises(ValueError, match="除数不能为零"):
        Calculator().divide(10, 0)