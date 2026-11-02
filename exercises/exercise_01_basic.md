# 练习 1：基础测试

## 目标
为以下模块编写完整的 pytest 测试。

## 待测代码

```python
# src/string_utils.py（你需要先创建这个文件）

def reverse_string(s: str) -> str:
    """反转字符串"""
    return s[::-1]


def is_palindrome(s: str) -> bool:
    """判断是否为回文（忽略大小写和空格）"""
    cleaned = s.replace(" ", "").lower()
    return cleaned == cleaned[::-1]


def count_vowels(s: str) -> int:
    """统计元音字母数量"""
    return sum(1 for c in s.lower() if c in "aeiou")


def truncate(s: str, max_len: int, suffix: str = "...") -> str:
    """截断字符串并添加后缀"""
    if len(s) <= max_len:
        return s
    return s[: max_len - len(suffix)] + suffix
```

## 任务

1. 创建 `src/string_utils.py`
2. 创建 `tests/test_string_utils.py`
3. 为每个函数至少编写 3 个测试用例（正常值、边界值、异常值）
4. 至少使用一次 `@pytest.mark.parametrize`
5. 运行 `pytest tests/test_string_utils.py -v` 确认全部通过

## 提示
- `reverse_string("")` 应该返回 `""`
- `is_palindrome("A man a plan a canal Panama")` 应该返回 `True`
- `truncate("hello", 10)` 不应该截断
- `truncate("hello world", 8)` 应该返回 `"hello..."`
