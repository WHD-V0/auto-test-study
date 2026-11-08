# 接口自动化测试：从入门到项目交付

目标：面对一份接口需求，能设计用例、准备数据、编写稳定的自动化测试，并根据失败证据定位问题。适合具备 Python 函数、类、异常、文件操作基础的学习者；零基础请先补这些知识。

本项目是实战训练样例，不是通用生产框架，也不承诺固定时间达到岗位要求。建议按 [学习路线](ROADMAP.md) 的九个阶段推进，每个阶段约一周、每天 1—2 小时；以验收结果决定是否进入下一阶段。

## 不知道每天怎么学，从这里开始

打开 [每日操作与验收手册](docs/daily/README.md)，按九阶段共 63 个学习日练习。每天都有指定材料、具体操作、运行命令、预期结果、完成勾选和卡点处理；学习日可以分多次完成，不要求按日历赶进度。

第一次学习直接看 [第 1 天：写出并运行第一个测试](docs/daily/01-python-pytest.md#day-1)：先自己写测试，再故意制造一次失败、看懂原因、恢复重跑。记录模板和“什么才算完成”见 [每日手册](docs/daily/README.md#如何判定自己完成了)。样例跑绿只表示基线通过，还要完成当天自写任务与验收。

## 主线与目录

| 路径 | 学习用途 |
|---|---|
| `src/`、`tests/test_*.py` | 保留的 pytest 基础、fixture、参数化、Mock 范例 |
| `sandbox/task_api.py` | 本地业务靶场：HTTP + SQLite，登录、权限、任务 CRUD |
| `tests/workflow/` | 实战主线：真实本地 HTTP、业务闭环、边界与越权测试 |
| `core/`、`config/` | 请求封装、结构断言、环境配置 |
| `tests/api/test_responses_mock.py` | 客户端离线测试，验证请求构造与异常包装 |
| `tests/test_client_contract.py` | 客户端重试、日志与状态码行为的回归测试 |
| `tests/api/*real.py`、`test_data_driven.py` | 公共接口扩展练习，需要外网 |
| `docs/` | 接口契约、用例设计、故障定位和交付验收 |
| `docs/daily/` | 63 个学习日的动手步骤、命令、完成标准与卡点处理 |
| `exercises/` | 各阶段作业（含 SQL、Linux、JMeter） |
| `sql/`、`tools/sql_lab.py` | 独立 SQL 训练数据与只读查询 |
| `scripts/run_regression.sh` | Linux/Bash 回归、报告与失败退出码 |
| `performance/`、`tools/check_jtl.py` | JMeter 业务链路、结果校验与报告模板 |
| `.github/workflows/tests.yml` | Linux / Windows 本地回归与报告归档 |

这里有三种不同的测试：单元测试验证函数或类；responses 测试验证客户端如何构造请求和处理响应，不能证明服务端正确；本地集成测试通过真实 HTTP 验证靶场的权限、校验和数据变化。公共 API 只作补充，不是日常回归的前提。

## 快速开始（Windows PowerShell）

建议 Python 3.11。以下命令在项目根目录执行，不依赖虚拟环境激活脚本：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# 默认运行基础测试、Mock 测试和本地集成测试，不访问公共 API
.\.venv\Scripts\python.exe -m pytest
# 只学习真实业务测试（测试自动启动本地服务，不要另开服务器）
.\.venv\Scripts\python.exe -m pytest tests/workflow -v
# 回归报告 + CI 可读的 JUnit 结果
.\.venv\Scripts\python.exe -m pytest --html=reports/report.html --self-contained-html --junitxml=reports/junit.xml
# 验证并行隔离；学习时先用两个进程
.\.venv\Scripts\python.exe -m pytest -n 2
```

macOS / Linux 创建环境使用 `python3.11 -m venv .venv`，之后把解释器路径换成 `.venv/bin/python`。依赖采用版本范围；CI 会归档实际安装版本，正式项目应按团队工具维护锁文件。

## 先体验一个真实业务闭环

1. 阅读 [接口契约](docs/API_CONTRACT.md)，先列出“什么情况下应该返回什么”。
2. 阅读 [用例设计](docs/TEST_DESIGN.md)，理解测试为什么覆盖这些场景。
3. 运行 `tests/workflow/test_tasks.py`：登录 → 创建任务 → 用返回的 ID 查询 → 更新 → 再次查询确认 → 删除 → 查询确认 404。
4. 修改靶场的一条业务规则，观察对应测试能否发现问题；恢复后再提交。
5. 按 [排障指南](docs/DEBUGGING.md) 写出失败证据与原因，而不只记录“用例失败”。

测试为每个 worker 启动独立服务、使用独立临时 SQLite 数据库；客户端和 token 按用例隔离，已创建资源通过 fixture 清理。数据库支持跨请求、进程重启后的持久化；测试结束会清理临时数据。

## 手动调试靶场（可选）

```powershell
.\.venv\Scripts\python.exe -m sandbox.task_api --port 8765 --db reports/tasks.sqlite3
```

手动服务地址是 `http://127.0.0.1:8765`。演示账号见接口契约，仅供本机练习。该服务只绑定回环地址，使用简化的演示登录，不提供生产鉴权能力。

## 环境切换与外网扩展

本地集成测试的地址由 fixture 动态注入，不受 `TEST_ENV` 影响。配置中的 test/dev 供公共接口范例练习使用，两者目前指向同一个公共站点，并不代表两套独立部署。

```powershell
$env:TEST_ENV = 'dev'
.\.venv\Scripts\python.exe -m pytest tests/api -m real_api
Remove-Item Env:TEST_ENV
```

Bash 对应：`TEST_ENV=dev .venv/bin/python -m pytest tests/api -m real_api`。

默认配置包含 `-m 'not real_api'`；显式 `-m real_api` 会覆盖它。JSONPlaceholder 的写入不持久化，不能用于验证业务闭环；Reqres 的 API key、套餐和接口行为需要以当前文档为准，现有主线不依赖它。

## 完成后应该交付什么

接口风险清单、可追溯的用例设计、能独立运行并清理数据的测试、CI 结果与报告、至少一份有证据的缺陷报告。具体标准见 [交付检查](docs/DELIVERY.md)。先掌握这些，再考虑是否需要增加框架抽象。

## SQL、Linux、JMeter 三项工作技能

| 模块 | 学什么 | 从哪里开始 |
|---|---|---|
| SQL | 关联/聚合、NULL、事务、索引基础、只读落库核对 | [SQL 章节](docs/SQL.md) → [练习 05](exercises/exercise_05_sql.md) |
| Linux | 进程/端口/HTTP/日志排障、Bash 回归与退出码 | [Linux 章节](docs/LINUX.md) → [练习 06](exercises/exercise_06_linux.md) |
| JMeter | token/ID 关联、断言、非 GUI、小规模负载与指标 | [JMeter 章节](docs/JMETER.md) → [练习 07](exercises/exercise_07_jmeter.md) |

SQL/Linux 是接口测试常见基础，JMeter 对应常见性能测试工作；具体岗位工具会有差异。课程先让你在本地做出证据，不把玩具靶场等同于生产系统。

## 教程最后：我学会了什么，如何写进简历

先用 [学习成果与能力验收](docs/LEARNING_OUTCOMES.md) 检查自己能否独立完成，再看 [简历与面试](docs/RESUME_INTERVIEW.md)。最后一章提供技能栏、个人项目模板、数字的证据来源、两分钟项目介绍和高频追问；必须按个人实际完成范围填写。

维护验证的实际范围见 [验证记录](docs/VALIDATION.md)，其中明确标注尚未执行的 Linux/JMeter/远程 CI 项目。
