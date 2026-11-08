#!/usr/bin/env bash
set -euo pipefail
source exercises/linux/common.sh
require_own_service
date -Iseconds
if curl --fail-with-body --max-time 3 -sS -i -H 'Authorization: Bearer invalid-lesson-token' http://127.0.0.1:8765/tasks > "$lesson_reports/wrong-token.txt"; then
    echo '预期401却成功' >&2; exit 1
else
    lesson_auth_exit=$?
    printf 'auth_curl_exit=%s\n' "$lesson_auth_exit"
fi
cat "$lesson_reports/wrong-token.txt"
grep -q '401' "$lesson_reports/wrong-token.txt"
grep -q 'unauthorized' "$lesson_reports/wrong-token.txt"
curl --max-time 3 -fsS http://127.0.0.1:8765/health
df -h .
du -sh reports/learning
free -m
ps -p "$lesson_service_pid" -o pid,etime,%cpu,%mem,args
