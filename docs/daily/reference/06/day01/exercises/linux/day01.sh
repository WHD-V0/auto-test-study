#!/usr/bin/env bash
set -euo pipefail
# 在Linux项目根目录运行，不能在PowerShell执行。
pwd
ls -la
id
cat /etc/os-release
python3 --version
if [[ ! -x .venv-linux/bin/python ]]; then
    python3 -m venv .venv-linux
fi
.venv-linux/bin/python -m pip install -r requirements.txt
.venv-linux/bin/python -m pytest tests/test_calculator.py -q
