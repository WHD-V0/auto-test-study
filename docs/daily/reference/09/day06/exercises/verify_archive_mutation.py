from pathlib import Path
import subprocess
import sys

target = Path("sandbox/task_api.py")
original = target.read_bytes()
source = original.decode("utf-8")
old = "query += \" AND status != 'archived'\""
assert source.count(old) == 1, "请先完成第4天默认过滤实现"
args = [sys.executable, "-B", "-m", "pytest", "tests/workflow/test_archive.py",
        "-k", "default_list", "-q"]
subprocess.run(args, check=True)
try:
    target.write_text(source.replace(old, 'query += ""', 1), encoding="utf-8")
    assert subprocess.run(args).returncode == 1
finally:
    target.write_bytes(original)
subprocess.run(args, check=True)
print("归档列表泄漏缺陷已检出，源码已恢复")
