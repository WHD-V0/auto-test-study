#!/usr/bin/env bash
set -euo pipefail
source exercises/linux/common.sh
if curl --max-time 1 -fsS http://127.0.0.1:8765/health >/dev/null 2>&1; then
    echo '8765已有服务，先核对并处理占用者；本脚本不结束已有进程' >&2
    exit 1
fi
nohup "$lesson_python" -u -m sandbox.task_api --port 8765 --db "$lesson_db" > "$lesson_reports/service.log" 2>&1 &
lesson_service_pid=$!
printf '%s\n' "$lesson_service_pid" > "$lesson_reports/service.pid"
for lesson_attempt in {1..30}; do
    if ! kill -0 "$lesson_service_pid" 2>/dev/null; then
        tail -n 30 "$lesson_reports/service.log"
        exit 1
    fi
    if curl --max-time 1 -fsS http://127.0.0.1:8765/health; then
        require_own_service
        ss -lntp | grep ':8765'
        exit 0
    fi
    sleep 0.1
done
echo '服务未在就绪预算内启动，请查service.log' >&2
exit 1
