import pytest


def test_add_floats():
    assert Calculator().add(0.1, 0.2) == pytest.approx(0.3)


def test_divide_by_zero():
    with pytest.raises(ValueError, match="除数不能为零"):
        Calculator().divide(10, 0)
