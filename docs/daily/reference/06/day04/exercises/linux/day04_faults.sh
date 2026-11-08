#!/usr/bin/env bash
set -euo pipefail
source exercises/linux/common.sh
require_own_service
curl --max-time 2 -fsS http://127.0.0.1:8765/health
# 原服务运行时再绑定同端口，timeout防止错误情况下长时间阻塞。
if timeout 5 "$lesson_python" -m sandbox.task_api --port 8765 --db "$lesson_reports/conflict.sqlite3" > "$lesson_reports/conflict.log" 2>&1; then
    echo '预期端口占用失败，却启动成功' >&2; exit 1
else
    lesson_conflict_exit=$?
    [[ "$lesson_conflict_exit" -ne 124 ]] || { echo '未出现预期绑定失败，需查原因' >&2; exit 1; }
    printf 'conflict_exit=%s\n' "$lesson_conflict_exit"
    tail -n 15 "$lesson_reports/conflict.log"
fi
ss -lntp | grep ':8765'
require_own_service
kill -TERM "$lesson_service_pid"
for lesson_attempt in {1..30}; do
    if ! kill -0 "$lesson_service_pid" 2>/dev/null; then break; fi
    sleep 0.1
done
if curl --connect-timeout 1 --max-time 2 -fsS http://127.0.0.1:8765/health; then
    echo '停止后仍有HTTP响应，需重新核对占用者' >&2; exit 1
else
    lesson_curl_exit=$?
    printf 'stopped_service_curl_exit=%s\n' "$lesson_curl_exit"
fi
# 明确恢复服务，再交给第5天继续使用。
bash exercises/linux/start_service.sh
