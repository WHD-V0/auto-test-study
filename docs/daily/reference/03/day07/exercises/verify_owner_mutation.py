from pathlib import Path
import subprocess
import sys

target = Path("sandbox/task_api.py")
original = target.read_bytes()
source = original.decode("utf-8")
old = 'if row["owner"] != username:'
assert source.count(old) == 1
args = [sys.executable, "-B", "-m", "pytest", "tests/workflow/test_tasks_extended.py",
        "-k", "other_user", "-q"]
subprocess.run(args, check=True)
try:
    target.write_text(source.replace(old, "if False:", 1), encoding="utf-8")
    result = subprocess.run(args)
    assert result.returncode == 1, "移除权限判断后，应在期望403处失败"
finally:
    target.write_bytes(original)
subprocess.run(args, check=True)
print("越权缺陷已捕获；源码恢复，权限回归通过")
