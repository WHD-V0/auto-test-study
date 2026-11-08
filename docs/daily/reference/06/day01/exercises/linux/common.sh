#!/usr/bin/env bash
lesson_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd -- "$lesson_root"
lesson_python="${LESSON_PYTHON:-$lesson_root/.venv-linux/bin/python}"
lesson_reports="$lesson_root/reports/learning/linux"
lesson_db="$lesson_reports/manual.sqlite3"
mkdir -p -- "$lesson_reports"
if [[ ! -x "$lesson_python" ]]; then
    printf 'Linux解释器不存在: %s\n' "$lesson_python" >&2
    exit 1
fi

require_own_service() {
    read -r lesson_service_pid < "$lesson_reports/service.pid"
    [[ "$lesson_service_pid" =~ ^[0-9]+$ ]] || { echo 'PID无效' >&2; exit 1; }
    lesson_service_args="$(ps -p "$lesson_service_pid" -o args=)"
    [[ "$lesson_service_args" == *"sandbox.task_api"* && "$lesson_service_args" == *"$lesson_db"* ]] || {
        echo 'PID不再对应本次服务，拒绝停止' >&2; exit 1;
    }
    printf '已核对进程: %s %s\n' "$lesson_service_pid" "$lesson_service_args"
}
