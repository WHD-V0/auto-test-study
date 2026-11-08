from pathlib import Path
import subprocess
import sys

target = Path("sandbox/task_api.py")
original = target.read_bytes()
source = original.decode("utf-8")
old = "len(title.strip()) <= 80"
assert source.count(old) == 1
args = [sys.executable, "-B", "-m", "pytest", "tests/workflow/test_title81_reference.py", "-q"]
subprocess.run(args, check=True)
try:
    target.write_text(source.replace(old, "len(title.strip()) <= 81", 1), encoding="utf-8")
    assert subprocess.run(args).returncode == 1
finally:
    target.write_bytes(original)
subprocess.run(args, check=True)
print("81字符错误放行已被发现，服务源码已恢复")
