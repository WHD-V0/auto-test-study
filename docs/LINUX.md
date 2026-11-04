# Linux：运行回归与定位环境问题

对应阶段六、练习 06。目标：进入项目、运行测试、找到进程/端口/日志证据，保留失败退出码。不是要求先成为 Linux 运维工程师。

## 1. 环境与路径

使用 WSL2 Ubuntu、Linux 虚拟机或自己的测试机。Git Bash 可以练部分 Shell，但不能代替 Linux 的进程和网络排障。Windows 当前项目在 WSL 中通常是 `/mnt/d/pythonProject/auto-test-study`；实际以自己的挂载路径为准。WSL 需要自行安装并初始化发行版。

Windows `.venv` 不能直接在 Linux 使用。建议在 Linux 家目录 clone 一份自己的仓库并新建环境；靶场和压测客户端运行在同一系统/网络命名空间，避免跨 WSL/Windows 回环地址混淆。

```bash
pwd
ls -la
# 进入你在 Linux 上的项目目录后运行
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
bash scripts/run_regression.sh
```

使用 Python 3.11 或更新版本；本项目 CI 的基准版本为 3.11。发行版缺少 venv/curl/ss/sqlite3 时，按其包管理方式安装；Ubuntu 常用包为 python3-venv、curl、iproute2、procps、sqlite3。Python 版本来源应遵循你所在环境的约定。

## 2. 高频命令按任务学习

| 任务 | 命令 | 应解释什么 |
|---|---|---|
| 位置与权限 | pwd、ls -la、cd、id | 当前用户、相对路径、文件所有者 |
| 找文件和内容 | find、grep -nE、rg（如已装） | 文件名搜索与内容搜索的区别 |
| 查日志 | less、tail -n 50、tail -f | 时间、失败节点、上下文 |
| 查进程 | ps -ef、ps -p PID -o pid,etime,args | 是否是本次启动的服务 |
| 查监听 | ss -lntp | 端口、监听地址、对应进程；权限不足时信息可能不全 |
| 验证 HTTP | curl -i、curl -v | HTTP 错误与连接失败区别 |
| 查资源 | df -h .、du -sh reports、free -m、top | 磁盘、内存、CPU 是证据，不是单看一个数就定根因 |
| 停止进程 | kill -TERM PID | 核对命令行和 PID 后再停止自己启动的进程 |

```bash
find tests -name 'test_*.py'
grep -nE 'FAILED|ERROR|APIError' reports/linux/pytest.log
tail -n 50 reports/linux/pytest.log
ss -lntp
```

grep 没匹配时退出码为 1，不等于文件损坏。日志路径来自脚本；服务正常访问日志在本靶场被关闭，不应期待在服务日志中找到每次 HTTP 请求。

## 3. 手动启动与端口排障

```bash
mkdir -p reports
nohup .venv/bin/python -u -m sandbox.task_api --port 8765 --db reports/linux-tasks.sqlite3 > reports/task-api.log 2>&1 &
task_api_pid=$!
printf '%s\n' "$task_api_pid" > reports/task-api.pid
ps -p "$task_api_pid" -o pid,etime,args
ss -lntp | grep ':8765'
curl --fail-with-body -sS http://127.0.0.1:8765/health
```

不要紧接着假设启动完成：如果 curl 暂时连不上，先看进程和日志，再重试健康检查；自动化启动流程应带有有限时长的就绪轮询。此处手动服务用于 curl/JMeter，不是 pytest fixture 的服务。

- Connection refused：先核对服务、端口和当前系统，检查是否在另一个容器/WSL 内运行。
- Address already in use：查占用 PID，核对它是否属于自己；可选择另一个端口，不能批量杀所有 Python 进程。
- 401/403：连接已成功，检查登录和用户权限；增加超时不能修复鉴权。
- Permission denied：检查路径权限或脚本换行，不要一律 sudo。

停止前再次核对：`ps -p "$task_api_pid" -o pid,args`，确认确实是本次靶场，然后 `kill -TERM "$task_api_pid"`。新终端可以从 reports/task-api.pid 读取，但必须防止过期 PID 指向别的进程。

## 4. 回归脚本与退出码

`scripts/run_regression.sh` 使用项目目录定位、带引号的路径、`set -euo pipefail`；支持 `PYTHON_BIN`、`PYTEST_WORKERS`、`REPORT_DIR`，把 HTML、JUnit、依赖版本和终端日志保存到报告目录。

```bash
bash -n scripts/run_regression.sh
PYTEST_WORKERS=2 bash scripts/run_regression.sh tests/workflow
# 紧接上条命令查看；实际 CI 直接使用脚本退出状态
printf 'exit=%s\n' "$?"
```

解释 `>` 覆盖、`>>` 追加、`2>&1` 合并 stderr、`| tee` 同时保存输出。没有 pipefail 时，pytest 失败可能被最后成功的 tee 隐藏。阅读脚本，故意传入不存在的测试路径，验证脚本非零退出且留下日志；随后正常回归确认恢复。

脚本按 Bash 编写并保存为 LF。用 `bash script.sh` 不要求可执行位；若需要 `./script.sh` 再设置 `chmod u+x`。Windows PowerShell 语法不能直接粘进 Bash。

## 5. 故障记录

至少完成服务未启动、端口占用、错误 token、错误测试路径四种实验。每次记录：现象、命令、输出/退出码、假设、验证动作和结论。区分已确认原因与尚待排查的猜测；不得只写“Linux 上跑通了”。

验收：在真实 Linux/WSL 环境独立跑回归，说明服务/数据库/报告位置；使用进程、端口、HTTP 和测试日志解释一次失败；脚本失败能让 CI 失败。
