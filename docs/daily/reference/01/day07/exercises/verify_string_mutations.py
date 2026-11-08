from pathlib import Path
import subprocess
import sys

target = Path("src/string_utils.py")
original = target.read_bytes()
source = original.decode("utf-8")
experiments = [
    ("if not isinstance(s, str):", "if False:", "reverse_rejects_list"),
    ("if max_len < 0:", "if False:", "truncate_negative_limit"),
]
try:
    for old, new, selector in experiments:
        assert old in source, f"找不到待修改代码: {old}"
        target.write_text(source.replace(old, new, 1), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", "-m", "pytest",
            "tests/test_string_utils.py", "-k", selector, "-q", "-p", "no:cacheprovider"])
        assert result.returncode == 1, "应因目标断言失败，而非收集或环境错误"
        target.write_bytes(original)
finally:
    target.write_bytes(original)
subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/test_string_utils.py",
                "tests/test_week01_review.py", "-q"], check=True)
print("两种缺陷均被捕获，源码已恢复")
