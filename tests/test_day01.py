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
