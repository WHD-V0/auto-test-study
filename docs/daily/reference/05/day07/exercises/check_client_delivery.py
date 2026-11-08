import subprocess
import sys

subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/test_client_extended.py",
    "tests/test_client_contract.py", "tests/api/test_responses_mock.py", "-q"], check=True)
print("客户端扩展与基线回归通过；诊断故意失败文件未纳入默认收集")
