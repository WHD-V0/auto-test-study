#!/usr/bin/env bash
set -euo pipefail
source exercises/linux/common.sh
if PYTHON_BIN="$lesson_python" REPORT_DIR="$lesson_reports/bad-path" bash scripts/run_regression.sh tests/does_not_exist.py; then
    echo '错误路径却成功，检查退出码传递' >&2; exit 1
else
    lesson_bad_exit=$?
    printf 'bad_path_exit=%s\n' "$lesson_bad_exit"
fi
test -s "$lesson_reports/bad-path/pytest.log"
tail -n 20 "$lesson_reports/bad-path/pytest.log"
PYTHON_BIN="$lesson_python" REPORT_DIR="$lesson_reports/recovered" bash scripts/run_regression.sh tests/workflow
echo 'recovered_exit=0'
if (set +o pipefail; false | tee /dev/null); then
    echo '未启用pipefail时，tee的0遮住false的非零'
fi
if (set -o pipefail; false | tee /dev/null); then
    echo 'pipefail实验异常' >&2; exit 1
else
    echo '启用pipefail后，管道保留非零'
fi
