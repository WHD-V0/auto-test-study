#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$project_root"

python_bin="${PYTHON_BIN:-$project_root/.venv/bin/python}"
if [[ ! -x "$python_bin" ]]; then
    python_bin="${PYTHON_BIN:-python3}"
fi
report_dir="${REPORT_DIR:-$project_root/reports/linux}"
mkdir -p -- "$report_dir"

"$python_bin" --version
"$python_bin" -m pip freeze > "$report_dir/installed-requirements.txt"
# pipefail 保留 pytest 失败退出码；所有路径和透传参数都保持引用。
"$python_bin" -m pytest -n "${PYTEST_WORKERS:-2}" \
    --html="$report_dir/report.html" --self-contained-html \
    --junitxml="$report_dir/junit.xml" "$@" 2>&1 | tee "$report_dir/pytest.log"
