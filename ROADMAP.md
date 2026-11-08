# 接口自动化实战学习路线

建议九个阶段，每阶段约一周，每天 1—2 小时。会 pytest 的人可按验收跳过第一阶段；Python 零基础应先补语言基础。时间仅供安排，未通过验收就继续练习，不以“读完代码”作为完成标准。

学习循环：读需求 → 设计预期 → 编写测试 → 注入缺陷验证测试有效 → 排查失败 → 回归 → 提交成果。

本文件用于看阶段目标；每天具体打开什么、写什么、运行什么、怎样判定完成，请使用 [每日操作与验收手册](docs/daily/README.md)。编号“3-2”代表阶段三第 2 天。每阶段七个学习日，共 63 天；不按日历强行推进，完成当天勾选与证据再进入下一天。第一次从 [1-1：第一条测试](docs/daily/01-python-pytest.md#day-1) 开始。

## 阶段一：Python 与 pytest 基础

逐日操作：[第 1 天](docs/daily/01-python-pytest.md#day-1) · [第 2 天](docs/daily/01-python-pytest.md#day-2) · [第 3 天](docs/daily/01-python-pytest.md#day-3) · [第 4 天](docs/daily/01-python-pytest.md#day-4) · [第 5 天](docs/daily/01-python-pytest.md#day-5) · [第 6 天](docs/daily/01-python-pytest.md#day-6) · [第 7 天](docs/daily/01-python-pytest.md#day-7)。

材料：`src/`、`tests/test_calculator.py`、`tests/test_user_service.py`、`tests/test_parametrize.py`、练习 01。

- Day 1—2：断言、异常、浮点比较；区分业务预期与当前实现。
- Day 3—4：fixture 的依赖、yield 清理、function/session 作用域、tmp_path。实际写一次清理代码，不只返回对象。
- Day 5：参数化、可读的 ids、单用例失败时如何定位哪组数据。
- Day 6—7：truncate 边界与异常；`-k`、`-x`、`--tb=short` 定位失败；闭卷复写与缺陷注入验收。`--collect-only` 在 Day 5 参数化时先练。

交付：练习 01 的实现与测试，解释一处需求边界。验收：不抄样例写出正常、边界、异常测试；故意改坏实现后测试会失败。

## 阶段二：HTTP 与用例设计

逐日操作：[HTTP、手工验证与用例设计的七天步骤](docs/daily/02-http-design.md)。

材料：`docs/API_CONTRACT.md`、`docs/TEST_DESIGN.md`、本地靶场，练习 03 的设计部分。

- Day 1—2：请求方法、URL、query、JSON、headers、401/403/404/409/5xx、204 空响应。
- Day 3—4：按等价类、边界、权限矩阵和状态变化写测试设计。没有文档依据的预期先提问，不根据返回结果猜需求。
- Day 5：手动运行靶场，观察创建后再查询、重启后再查询的区别。
- Day 6—7：把一次手工验证变成自动测试，分别断言状态码、结构、业务值与副作用。

交付：至少 12 条用例，包含编号、需求、前置、输入、预期和优先级。验收：能说明为什么选这些用例、缺少哪些覆盖；正常返回不能证明越权保护生效。

## 阶段三：独立、可清理的业务测试

逐日操作：[业务闭环、权限、清理与并行的七天步骤](docs/daily/03-workflow.md)。

材料：`tests/workflow/conftest.py`、`tests/workflow/test_tasks.py`、练习 03。

- Day 1：通过真实 HTTP 完成同一资源的 CRUD；更新和删除都再读一次确认。
- Day 2：登录 fixture、两个用户的 token 隔离、401 与 403 的区别。
- Day 3：列表中校验所有元素、Schema、用户隔离、排序与删除副作用；Schema 通过不等于业务正确。
- Day 4：唯一测试数据、创建工厂与 yield 清理。测试中途断言失败也应清理已经创建的资源。
- Day 5：输入边界、未知字段、非法 JSON 和更新原子性。
- Day 6—7：单独运行、重复运行、调换顺序、`-n 2`；排查硬编码 ID 和共享状态。

交付：至少 12 条本地业务测试。验收：不依赖前一个测试创建数据；不访问公共网络；清理逻辑允许测试已删除的资源返回 404。

## 阶段四：SQL 与接口数据核对

逐日操作：[查询、事务、索引与落库核对的七天步骤](docs/daily/04-sql.md)。

材料：[SQL 实战](docs/SQL.md)、练习 05、`sql/`、`tests/workflow/test_database_checks.py`。

- Day 1—2：SELECT、WHERE、排序、LIKE、IN、NULL；明确查询对象与业务预期。
- Day 3—4：JOIN、GROUP BY/HAVING、重复计数、缺失关联数据。
- Day 5：事务提交/回滚、索引与 EXPLAIN 基础。
- Day 6—7：只读连接、参数绑定；为接口加落库断言，核对非法更新未部分写入。

交付：至少 8 条独立查询及预期结果、事务实验和一个新增落库断言。验收：能解释零任务用户、NULL 与空串、LEFT JOIN 计数；知道 SQLite 到 MySQL 需重新验证什么。

## 阶段五：客户端、Mock 与失败定位

逐日操作：[客户端测试、故障实验与缺陷报告的七天步骤](docs/daily/05-client-mock.md)。

材料：`core/api_client.py`、`tests/test_client_contract.py`、`tests/api/test_responses_mock.py`、`docs/DEBUGGING.md`、练习 02。

- Day 1—2：先直接使用 requests，再解释统一入口消除了什么重复；区分网络异常、HTTP 异常、JSON 解析失败和业务断言失败。
- Day 3：patch 与 responses 的边界。Mock 能验证客户端行为，不能证明远端遵守契约。
- Day 4：GET 的 503 重试、POST 不自动重放；请求重试和 pytest 整条用例重跑的副作用不同。
- Day 5：日志不记录凭据与响应正文；本地查看必要证据，输出前脱敏。
- Day 6—7：完成三次故障实验：非法响应、错误状态码、业务规则被改坏；分别给出定位依据。

交付：练习 02 和至少一份缺陷报告。验收：不使用“加重试后绿了”作为根因解释；能区分客户端、服务端、测试数据和环境问题。

## 阶段六：Linux 与回归排障

逐日操作：[Linux 环境、四种故障与回归脚本的七天步骤](docs/daily/06-linux.md)。

材料：[Linux 实战](docs/LINUX.md)、练习 06、`scripts/run_regression.sh`。

- Day 1—2：Linux/WSL 环境、目录、权限、专用虚拟环境与首次脚本回归；不要复用 Windows venv。
- Day 3—4：进程、监听端口、curl 与日志；演练服务未启动和端口冲突。
- Day 5：资源观察、错误 token 与业务故障的区别。
- Day 6—7：Bash 引用、重定向、tee 与 pipefail；验证失败退出码。

交付：Linux 上的一次正常回归和四份故障记录。验收：不用重启或批量 kill 代替定位；测试失败能传递给脚本和 CI。

## 阶段七：CI 与稳定回归

逐日操作：[报告、成功/失败 CI 与复现交付的七天步骤](docs/daily/07-ci.md)。

材料：`.github/workflows/tests.yml`、`pytest.ini`、`docs/DELIVERY.md`。

- Day 1：理解本地/公共 API 标记，默认回归不依赖外网服务。
- Day 2：生成并检查 HTML、JUnit 与实际安装版本；HTML 面向人工阅读，JUnit 面向 CI。
- Day 3：阅读 Linux / Windows CI，解释 Python 版本、依赖、执行命令、失败退出码。
- Day 4：在自己的仓库运行成功 CI，下载两个系统的报告。
- Day 5：故意失败 CI，验证失败后仍上传报告，再恢复通过。
- Day 6—7：两个 worker 隔离、最短复现、版本记录与干净环境交付。

交付：自己的仓库中一次成功 CI、一次故意失败 CI 及对应报告。验收：别人按 README 能跑通；失败不会被重试或忽略退出码掩盖。

## 阶段八：JMeter 与基础负载实验

逐日操作：[工具准备、关联、断言与对照报告的七天步骤](docs/daily/08-jmeter.md)。

材料：[JMeter 实战](docs/JMETER.md)、练习 07、`performance/`、`tools/check_jtl.py`。

- Day 1—2：工具与靶场准备、GUI 线程组、headers、token/ID 提取、HTTP/业务断言与预期 404。
- Day 3：非 GUI、JTL、HTML 报告与样本数量校验；进程退出 0 不代表断言全部通过。
- Day 4：故意改错断言，验证检查器非零退出，清理残留后恢复。
- Day 5：1/2/5 线程低负载对照，解释思考时间和请求比例。
- Day 6—7：按接口分析 P95、吞吐和错误率，结合环境证据填写报告。

交付：JMX、成功/故意失败的 JTL 与检查器结果、对照报告。验收：样本数量完整，失败被识别；不把本机教学靶场结果写成生产容量。

## 阶段九：需求变更与交付评审

逐日操作：[归档需求从设计到最终演示的七天步骤](docs/daily/09-delivery.md)。

材料：练习 04。

- Day 1：写一页设计说明，说明风险、取舍和不覆盖范围。
- Day 2—4：实现一个新业务需求，先补契约和用例设计，再实现并回归。
- Day 5：补鉴权、数据清理和旧功能回归，验证并行运行。
- Day 6—7：写缺陷报告和交付说明，演示测试如何发现故障。

交付：需求变更、代码、测试设计、CI、缺陷报告。验收：能讲清一条失败如何从现象定位到原因；能解释每个抽象的用途，不以目录数量或插件数量证明工作能力。

## 完成后的拓展顺序

1. 接入团队实际接口：OpenAPI、测试账号、授权范围、测试环境与数据回收。
2. 加入业务状态机、重复提交与幂等键；没有约定幂等机制前不自动重试写操作。
3. 学习数据库核对、异步任务轮询与超时预算、第三方依赖隔离。
4. 需要时再引入性能、安全、契约兼容性测试，这些不等同于当前功能测试。

面试准备应围绕自己的交付：测到了什么缺陷、为何这样设计、怎样避免互相污染、失败如何定位，以及哪些风险还没有覆盖。

## 教程最后：成果验收、简历与面试

1. 阅读 [学完后能做什么](docs/LEARNING_OUTCOMES.md)，用能力—证据表完成自查和综合考核。
2. 阅读 [简历与面试](docs/RESUME_INTERVIEW.md)，只保留自己完成的条目，填入真实贡献与测量结果。
3. 准备作品包：个人贡献、用例与代码、SQL/Linux 作业、CI、JMeter 原始数据和缺陷报告。

能讲清一个真实失败的定位过程，比宣称“精通所有工具”更有价值。
