# 阶段六：在 Linux 上跑回归并定位失败

[每日目录](README.md) · [上一阶段](05-client-mock.md) · [下一阶段](07-ci.md) · [Linux 讲解](../LINUX.md) · [练习 06](../../exercises/exercise_06_linux.md)

**本章代码块除特别标注外全部在 Linux Bash 执行。** 需要已初始化的 WSL2 Ubuntu、Linux 虚拟机或测试机。没有环境时先准备，阅读不能代替实操。本周结果写 `docs/linux_practice.md`，保留发行版、命令、输出、退出码和结论。

WSL 可进入 `/mnt/d/pythonProject/auto-test-study`。在这个 Windows 共享目录练习时专用环境叫 `.venv-linux`，不要覆盖 Windows `.venv`；若已在 Linux 家目录另有项目副本，同样可用 `.venv-linux` 跟本章命令一致。该环境目录应在本地 Git 排除文件中忽略，或向项目 `.gitignore` 添加 `.venv-linux/`，不提交虚拟环境。

<a id="day-1"></a>

## 第 1 天：确认系统与目录，创建 Linux 专用环境

**材料：** Linux 讲解第 1 节。

**操作：**

1. Windows 用户先在 PowerShell 执行 `wsl --list --verbose`，确认有自己的 Linux 发行版，再打开该发行版终端。未安装时按系统 WSL 安装向导完成并重启，今天可分两次做。
2. 在 Bash 中进入真实项目路径，执行以下命令，确认看到 README、tests、requirements.txt：

```bash
cd /mnt/d/pythonProject/auto-test-study
pwd
ls -la
id
cat /etc/os-release
python3 --version
```

非 WSL 用户将 cd 改为自己的 Linux 项目路径。推荐 Python 3.11；若缺 python3/venv/curl/ss，按 [Linux 讲解](../LINUX.md) 安装相应系统包后再继续。

```bash
python3 -m venv .venv-linux
.venv-linux/bin/python -m pip install -r requirements.txt
.venv-linux/bin/python -m pytest tests/test_calculator.py -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

day01是实际执行脚本，common为后续脚本定位根目录与专用环境。保存为LF换行，用bash运行即可，不要求chmod。脚本不安装WSL或系统包；环境缺失先完成本章环境准备。

文件 `exercises/linux/day01.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day01/exercises/linux/day01.sh)

```bash
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
```

文件 `exercises/linux/common.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day01/exercises/linux/common.sh)

```bash
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
```

**运行本日参考脚本（Linux项目根目录，Bash）：**

```bash
bash exercises/linux/day01.sh
```

**对照运行后的结果：** Linux解释器可用，计算器测试通过，记录真实发行版/Python/pwd；本次文档维护只检查Bash语法，不能替代你的Linux实操。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 记录 Linux 发行版、Python 版本、pwd、用户，计算器测试在 Linux 通过。
- [ ] 实际解释器路径是 `.venv-linux/bin/python`，没有调用 Windows Scripts/python.exe。
- [ ] 能区分 Windows 路径 `D:\...` 与 WSL 挂载路径 `/mnt/d/...`。

**卡住时：** 在 Linux 中看到 Windows `.venv` 不等于能用；权限问题先检查目录和所有者，不一律 sudo。

<a id="day-2"></a>

## 第 2 天：运行 Linux 回归，找到报告和日志

**材料：** `scripts/run_regression.sh` 的 PYTHON_BIN、REPORT_DIR。

**操作与运行：**

```bash
bash -n scripts/run_regression.sh
PYTHON_BIN="$PWD/.venv-linux/bin/python" REPORT_DIR="$PWD/reports/learning/linux-day02" bash scripts/run_regression.sh tests/workflow
printf 'exit=%s\n' "$?"
ls -lh reports/learning/linux-day02
tail -n 30 reports/learning/linux-day02/pytest.log
find tests/workflow -name 'test_*.py'
```

1. 确认报告目录有 HTML、JUnit、pytest.log、installed-requirements.txt。
2. 用 `grep -nE 'FAILED|ERROR' reports/learning/linux-day02/pytest.log` 找失败；没有匹配时 grep 返回 1，不等于 pytest 失败。若有失败，先定位再重跑。
3. 在记录中解释脚本里 `"$@"` 为什么要加引号，为什么要从脚本路径定位项目根目录。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

set -e使真正回归失败时脚本在打印成功前停止。grep是日志筛选，不用它的退出码代替pytest结果。PYTHON_BIN把Linux专用解释器传给现有脚本。

文件 `exercises/linux/day02.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day02/exercises/linux/day02.sh)

```bash
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
```

**运行本日参考脚本（Linux项目根目录，Bash）：**

```bash
bash exercises/linux/day02.sh
```

**对照运行后的结果：** 退出0，day02目录有report.html、junit.xml、pytest.log、installed-requirements.txt。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 真实 Linux workflow 回归退出 0，四类报告文件存在且能找到测试摘要。
- [ ] 记录该次报告路径和最短复现命令，不只贴“全绿”截图。
- [ ] 能说明 pytest 临时服务不需要手动启动，也不会复用手工库。

**卡住时：** 脚本找不到解释器时检查 PYTHON_BIN 的绝对路径；不要让它意外退回未装依赖的系统 Python。

<a id="day-3"></a>

## 第 3 天：自己启动服务，用进程、端口与 HTTP 确认就绪

**材料：** Linux 讲解第 2—3 节。

**操作：** 以下命令在同一个 Bash 终端执行；后台启动不会占住输入：

```bash
mkdir -p reports/learning
nohup .venv-linux/bin/python -u -m sandbox.task_api --port 8765 --db reports/learning/linux-manual.sqlite3 > reports/learning/linux-service.log 2>&1 &
task_api_pid=$!
ps -p "$task_api_pid" -o pid,etime,args
ss -lntp | grep ':8765'
curl --fail-with-body -sS http://127.0.0.1:8765/health
```

1. 首次 curl 若启动未完成，检查进程和 `tail` 日志后再试，不把一次连接失败当最终结论。
2. 记录 PID、命令行、监听地址和 health 正文；确认都指向本次服务。
3. 解释 `> ... 2>&1 &` 的各部分。服务关闭正常访问日志，因此日志没有每次请求记录是正常的。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

保存脚本后运行bash exercises/linux/start_service.sh。$!是本次后台进程PID，有限轮询检查服务真正就绪。PID写入文件供后续日使用，每次停止前还要核对命令行，不能盲信旧PID。

文件 `exercises/linux/start_service.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day03/exercises/linux/start_service.sh)

```bash
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
```

**运行本日参考脚本（Linux项目根目录，Bash）：**

```bash
bash exercises/linux/start_service.sh
```

**对照运行后的结果：** health正常，打印正确进程和8765监听；服务继续在后台运行。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 同一个服务有进程、127.0.0.1:8765 监听、health=200 三类证据。
- [ ] 能说明“进程存在”和“HTTP 服务已就绪”不是同一个检查。
- [ ] 保留这个终端和 `task_api_pid`，第 4 天继续使用。

**卡住时：** 新终端会丢失 PID 变量；重新核实 ps/ss，不凭记忆停止进程。

<a id="day-4"></a>

## 第 4 天：复现服务未启动与端口占用

**材料：** 练习 06 的前两种故障。

**操作：**

1. 保持昨天服务运行，另开 Linux 项目终端 B，用另一个数据库启动同端口：

```bash
.venv-linux/bin/python -m sandbox.task_api --port 8765 --db reports/learning/linux-conflict.sqlite3
printf 'exit=%s\n' "$?"
ss -lntp | grep ':8765'
```

预期新服务启动报地址占用、非零退出，原服务 health 仍可用。记清占用者是谁，不批量 kill。

2. 回到 A，先核对 PID 命令行，确认是自己第 3 天启动的靶场，再停止：

```bash
ps -p "$task_api_pid" -o pid,args
kill -TERM "$task_api_pid"
```

3. 等服务退出后再次核对端口与请求：

```bash
ss -lntp | grep ':8765'
curl --connect-timeout 2 --max-time 3 -sS http://127.0.0.1:8765/health
printf 'exit=%s\n' "$?"
```

curl 应连接失败、非零退出，区别于 HTTP 401。按第 3 天命令重启并验证 health 恢复。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

只有require_own_service确认本次靶场PID后才TERM。新服务绑定失败与停止后的curl连接失败是两种不同故障，分别留日志；脚本最后重启恢复。失败实验本身被验证后，教学脚本可以返回0。

文件 `exercises/linux/day04_faults.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day04/exercises/linux/day04_faults.sh)

```bash
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
```

**运行本日参考脚本（Linux项目根目录，Bash）：**

```bash
bash exercises/linux/day04_faults.sh
```

**对照运行后的结果：** 冲突进程非零且日志有地址占用；停服后curl非零；重启health恢复。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 两份故障记录分别有现象、命令、退出码、ps/ss/curl 证据、根因和恢复结果。
- [ ] 能解释冲突时新进程失败但旧服务仍能响应。
- [ ] 只停止核对过的自有进程。

**卡住时：** 如果 8765 的占用者不是自己，本次不结束它；为实验另选空闲端口，所有命令一起改。

<a id="day-5"></a>

## 第 5 天：错误 token 与资源观察

**材料：** 契约的认证规则，Linux 讲解第 2 节。

**操作：**

```bash
curl --fail-with-body -sS -i -H 'Authorization: Bearer invalid-lesson-token' http://127.0.0.1:8765/tasks
printf 'exit=%s\n' "$?"
curl --fail-with-body -sS http://127.0.0.1:8765/health
df -h .
du -sh reports/learning
free -m
ps -p "$task_api_pid" -o pid,etime,%cpu,%mem,args
```

1. 确认第一次是 HTTP 401、curl 非零退出（`--fail-with-body` 使 HTTP 错误也失败），第二次 health 正常。
2. 写第三份故障记录：连接成功、身份失败；列出为何增加 timeout 不会修复 token。
3. 记录同一时间点的磁盘、内存、进程资源，写出每个命令在观察什么；不能凭一个数认定数据库瓶颈。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

curl使用fail-with-body使401也成为非零退出，再核对401和unauthorized避免把网络失败误判为鉴权失败。health成功说明服务仍可用；资源观察只提供同时间窗证据。

文件 `exercises/linux/day05_auth.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day05/exercises/linux/day05_auth.sh)

```bash
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
```

**运行本日参考脚本（Linux项目根目录，Bash）：**

```bash
bash exercises/linux/day05_auth.sh
```

**对照运行后的结果：** 401+unauthorized、curl非零，health正常；磁盘/内存/CPU输出带日期。旧curl不支持选项时按原卡点说明调整。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 能用 401 响应和 health 区分鉴权错误与服务未启动。
- [ ] 第三份故障记录完整，资源观测带时间和单位。
- [ ] 能解释 curl 是否启用 fail 选项会影响 HTTP 错误的退出码。

**卡住时：** 若 curl 版本无 `--fail-with-body`，可用 `--fail` 检查非零退出，另用 `-i` 查看响应；在记录中写清版本和差异。

<a id="day-6"></a>

## 第 6 天：证明脚本不会把失败隐藏在 tee 后

**材料：** `scripts/run_regression.sh` 的 `set -euo pipefail` 与管道。

**操作：**

```bash
PYTHON_BIN="$PWD/.venv-linux/bin/python" REPORT_DIR="$PWD/reports/learning/linux-bad-path" bash scripts/run_regression.sh tests/does_not_exist.py
printf 'exit=%s\n' "$?"
tail -n 30 reports/learning/linux-bad-path/pytest.log
PYTHON_BIN="$PWD/.venv-linux/bin/python" REPORT_DIR="$PWD/reports/learning/linux-recovered" bash scripts/run_regression.sh tests/workflow
printf 'exit=%s\n' "$?"
```

1. 紧接失败命令查看退出码，避免被后续 ls/tail 覆盖。
2. 写第四份故障记录：错误测试路径导致 pytest usage error，脚本非零且保存日志；恢复后正确路径退出 0。
3. 用自己的话解释 `>`、`>>`、stderr、tee、pipefail。可以用 `false | tee /dev/null` 与子 shell `(set -o pipefail; false | tee /dev/null)` 对照退出码，别修改项目脚本取消 pipefail。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

if/else立即保存实际退出码，不能先跑tail再读$?。最后两个子shell仅演示管道退出行为，不修改项目脚本。正常回归失败仍由set-e暴露。

文件 `exercises/linux/day06_exit_codes.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day06/exercises/linux/day06_exit_codes.sh)

```bash
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
```

**运行本日参考脚本（Linux项目根目录，Bash）：**

```bash
bash exercises/linux/day06_exit_codes.sh
```

**对照运行后的结果：** 错误路径非零且有日志；正确路径0；pipefail对照符合文字说明。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 错路径非零、正常回归为 0，两份日志分开保存。
- [ ] 能解释没有 pipefail 时最后成功的 tee 为什么可能遮住 pytest 失败。
- [ ] 四种故障记录齐全，不把错误路径记录成产品缺陷。

**卡住时：** 有些 usage error 不会生成完整 HTML；本实验必须保留的是非零退出和终端日志，不能伪造报告。

<a id="day-7"></a>

## 第 7 天：独立复现一项故障并交付 Linux 记录

**操作：**

1. 不看昨天记录，自选“服务未启动/端口占用/错误 token/错误测试路径”之一，重新触发、定位并恢复。
2. 再完整跑一次脚本，输出到新报告目录，不只跑一条单元测试。
3. 汇总 OS/Python、服务/数据库/报告位置、四种故障及退出码、最终回归结果。最后核对并停止自己手动启动的服务。

```bash
PYTHON_BIN="$PWD/.venv-linux/bin/python" REPORT_DIR="$PWD/reports/learning/linux-final" bash scripts/run_regression.sh
printf 'exit=%s\n' "$?"
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

最终脚本跑完整默认回归，再停止核对过的服务。表格给出四种故障应如何写清，实际PID、版本、退出码与输出必须自己记录。

文件 `exercises/linux/day07_delivery.sh` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day07/exercises/linux/day07_delivery.sh)

```bash
#!/usr/bin/env bash
set -euo pipefail
source exercises/linux/common.sh
PYTHON_BIN="$lesson_python" REPORT_DIR="$lesson_reports/final" bash scripts/run_regression.sh
echo 'full_regression_exit=0'
require_own_service
kill -TERM "$lesson_service_pid"
echo '本周手动服务已发送TERM；报告在reports/learning/linux/final'
```

文件 `docs/linux_practice.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/06/day07/docs/linux_practice.md)

```markdown
# Linux排障记录参考成品结构

| 故障 | 触发 | 应取得的事实 | 已确认原因 | 恢复验证 |
|---|---|---|---|---|
| 未启动 | TERM本次服务后curl health | 无监听/连接失败、curl非零 | 目标服务已停止 | 重启health200 |
| 端口冲突 | 运行中再绑定8765 | 新进程非零、地址占用；旧PID仍监听 | 同地址端口已绑定 | 保留正确服务或换空闲端口 |
| 错误token | 伪造Bearer token GET tasks | HTTP401 unauthorized；health200 | 身份无效，非网络中断 | 重新合法登录 |
| 测试路径错误 | 脚本传不存在路径 | pytest非零、日志保存 | 输入路径不存在 | 正确目录回归0 |

本次实际发行版/Python/pwd/PID、时间、命令输出、退出码、完整回归报告：执行后逐项粘贴。
上表是预期与归因写法，不是已经在Linux执行过的证明。
```

**运行本日参考脚本（Linux项目根目录，Bash）：**

```bash
bash exercises/linux/day07_delivery.sh
```

**对照运行后的结果：** 完整Linux回归0，四种故障都有实际证据，本周手动服务已停止。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 完整回归在真实 Linux 退出 0，四份故障含恢复证据。
- [ ] 能不依赖重启机器或批量 kill 定位所选故障。
- [ ] `docs/linux_practice.md` 让别人按命令复现，未提交环境目录和数据库。

**未通过怎么办：** 缺环境先补第 1 天；分不清网络/HTTP 回第 3—5 天；退出码不对回第 6 天。
