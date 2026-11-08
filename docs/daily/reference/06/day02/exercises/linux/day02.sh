#!/usr/bin/env bash
set -euo pipefail
source exercises/linux/common.sh
bash -n scripts/run_regression.sh
PYTHON_BIN="$lesson_python" REPORT_DIR="$lesson_reports/day02" bash scripts/run_regression.sh tests/workflow
printf 'regression_exit=0\n'
ls -lh "$lesson_reports/day02"
tail -n 30 "$lesson_reports/day02/pytest.log"
# grep没匹配返回1是正常的，不能让它冒充回归失败。
if grep -nE 'FAILED|ERROR' "$lesson_reports/day02/pytest.log"; then
    echo '发现失败/错误文字，请检查上下文'
else
    echo '日志没有FAILED/ERROR匹配'
fi
find tests/workflow -name 'test_*.py'
