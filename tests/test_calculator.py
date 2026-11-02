"""基础测试示例 —— Calculator 模块
学习要点：
  - pytest 测试函数命名规范
  - 常用断言写法
  - 测试异常
"""
import pytest
from src.calculator import Calculator


@pytest.fixture
def calc():
    """每个测试函数都会得到一个新的 Calculator 实例"""
    return Calculator()


# ── 基础断言 ──────────────────────────────────

class TestAdd:
    def test_positive_numbers(self, calc):
        assert calc.add(2, 3) == 5

    def test_negative_numbers(self, calc):
        assert calc.add(-1, -1) == -2

    def test_mixed(self, calc):
        assert calc.add(-1, 1) == 0

    def test_floats(self, calc):
        assert calc.add(0.1, 0.2) == pytest.approx(0.3)


class TestSubtract:
    def test_basic(self, calc):
        assert calc.subtract(10, 3) == 7

    def test_result_negative(self, calc):
        assert calc.subtract(3, 10) == -7


class TestMultiply:
    def test_basic(self, calc):
        assert calc.multiply(3, 4) == 12

    def test_by_zero(self, calc):
        assert calc.multiply(5, 0) == 0


class TestDivide:
    def test_basic(self, calc):
        assert calc.divide(10, 2) == 5.0

    def test_float_result(self, calc):
        assert calc.divide(7, 2) == 3.5

    def test_divide_by_zero(self, calc):
        """学习：用 pytest.raises 测试异常"""
        with pytest.raises(ValueError, match="除数不能为零"):
            calc.divide(10, 0)
