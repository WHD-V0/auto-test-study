from src.calculator import Calculator


def test_add():
    calc = Calculator()
    actual = calc.add(2, 3)
    assert actual == 5


def test_add_negative_numbers():
    calc = Calculator()
    assert calc.add(-2, -3) == -5


def test_add_zero():
    calc = Calculator()
    assert calc.add(5, 0) == 5
