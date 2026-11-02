"""参数化测试示例
学习要点：
  - @pytest.mark.parametrize 数据驱动
  - 多组数据自动展开为多个测试用例
"""
import pytest
from src.calculator import Calculator


calc = Calculator()


class TestParametrize:
    """用参数化减少重复代码"""

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (1, 2, 3),
            (0, 0, 0),
            (-1, 1, 0),
            (100, 200, 300),
            (0.1, 0.2, 0.3),
        ],
    )
    def test_add(self, a, b, expected):
        assert calc.add(a, b) == pytest.approx(expected)

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (10, 5, 5),
            (0, 0, 0),
            (-3, -1, -2),
        ],
    )
    def test_subtract(self, a, b, expected):
        assert calc.subtract(a, b) == pytest.approx(expected)

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (2, 3, 6),
            (0, 999, 0),
            (-2, 3, -6),
        ],
    )
    def test_multiply(self, a, b, expected):
        assert calc.multiply(a, b) == pytest.approx(expected)

    @pytest.mark.parametrize(
        "a, b, expected",
        [
            (10, 2, 5.0),
            (7, 2, 3.5),
            (1, 3, pytest.approx(0.333, abs=1e-2)),
        ],
    )
    def test_divide(self, a, b, expected):
        assert calc.divide(a, b) == expected

    @pytest.mark.parametrize(
        "a, b",
        [
            (1, 0),
            (0, 0),
            (-5, 0),
        ],
    )
    def test_divide_by_zero(self, a, b):
        with pytest.raises(ValueError):
            calc.divide(a, b)
