#!/usr/bin/env bash
set -euo pipefail
source exercises/linux/common.sh
PYTHON_BIN="$lesson_python" REPORT_DIR="$lesson_reports/final" bash scripts/run_regression.sh
echo 'full_regression_exit=0'
require_own_service
kill -TERM "$lesson_service_pid"
echo '本周手动服务已发送TERM；报告在reports/learning/linux/final'
