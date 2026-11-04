# JMeter：从正确业务请求到可解释的负载结果

对应阶段八、练习 07。目标是会构造请求、关联 token/ID、做断言、用非 GUI 执行和分析结果。会用 JMeter 并不等于已经具备大型系统性能调优经验。

## 1. 工具与靶场

准备 Apache JMeter 5.6.3 和兼容的 Java（本教程示例使用 Java 17）。从 [Apache 官方下载页](https://jmeter.apache.org/download_jmeter.cgi) 获取并安装，运行 `java -version`、`jmeter -v` 记录实际版本。JMeter 不属于 pip 依赖。

先用虚拟环境解释器手动启动本机靶场：

```text
python -m sandbox.task_api --port 8765 --db reports/jmeter-tasks.sqlite3
```

等待 `/health` 返回 200。JMeter 和服务在同一台机器、同一系统内运行；默认只访问 127.0.0.1，不向公共 API 发送负载。SQLite + Python 标准库服务只用于方法训练，结果不能代表生产系统容量。

## 2. 阅读并运行提供的计划

打开 `performance/task_workflow.jmx`。结构是 Thread Group → 每线程仅一次的登录 → 每轮任务业务链路：创建、查询、更新、再次查询、删除、确认 404。

| 元件 | 作用 |
|---|---|
| HTTP Request Defaults | host/port、连接与响应超时 |
| Header Manager | JSON Content-Type，业务请求加 Bearer token |
| JSON Extractor | 每线程提取 auth_token，每轮提取 task_id，不能写死 |
| Response Assertion | 校验每个预期状态；预期的 404 也需要被判为成功 |
| JSR223 Assertion（Groovy） | 再查询后检查 status=done 和当前 task_id |
| Constant Timer | 每次业务请求前等待，模拟思考时间 |
| Thread Group | threads、ramp_up、loops；失败停止当前线程 |

token 与 id 是线程变量；标题含 run_id、线程号与计数器，避免测试数据混淆。默认 1 线程、3 轮、200ms 思考时间；每线程登录一次，每轮 6 个业务请求，因此默认应有 19 个样本。

GUI 适合检查计划和小流量调试；可在线程组下临时添加“监听器 → 查看结果树”，只在单线程调试时启用。先确认 1 线程所有断言正确，再用非 GUI 测试；负载运行不要开启 View Results Tree 等大量保存响应的监听器。

## 3. 非 GUI 命令

每次使用新的结果目录，JTL 不能混入上次数据，HTML 输出目录必须为空或不存在。以下目录名只是示例，第二次换名称。

Windows PowerShell（把路径改成自己的安装位置）：

```powershell
$jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat'
New-Item -ItemType Directory -Force reports/jmeter/smoke-01
& $jmeter -n -t performance/task_workflow.jmx -q performance/jmeter.properties -Jthreads=1 -Jloops=3 -Jramp_up=1 -Jthink_ms=200 -Jrun_id=smoke01 -l reports/jmeter/smoke-01/results.jtl -j reports/jmeter/smoke-01/jmeter.log -e -o reports/jmeter/smoke-01/html
```

Linux / Bash（jmeter 已加入 PATH）：

```bash
mkdir -p reports/jmeter/smoke-01
jmeter -n -t performance/task_workflow.jmx -q performance/jmeter.properties -Jthreads=1 -Jloops=3 -Jramp_up=1 -Jthink_ms=200 -Jrun_id=smoke01 -l reports/jmeter/smoke-01/results.jtl -j reports/jmeter/smoke-01/jmeter.log -e -o reports/jmeter/smoke-01/html
```

run_id 使用不超过 30 位的英文字母/数字/连字符；不要把原始用户输入直接填进 JSON 模板。host、port 可用 -Jhost/-Jport 修改。所有数字参数用正整数，think_ms 可以为 0。

JMeter 进程退出 0 不保证样本没有断言失败。执行后必须检查 JTL 的 success、样本数量和错误率；本项目提供检查器：

```text
python -m tools.check_jtl reports/jmeter/smoke-01/results.jtl --expected-samples 19
```

这个检查器是功能正确性门槛：缺失样本、错误样本、非法指标会非零退出；它还不是业务 SLA 门禁；检查器采用 nearest-rank P95，小样本时可能与 Dashboard 的插值结果不同。普通 pytest CI 不自动施压，避免把共享 runner 的波动误当成容量结论。

## 4. 先建立实验目标，再解释指标

训练目标示例：在同一环境、相同思考时间、相同业务比例下，比较 1 / 2 / 5 线程的现象。ramp-up 可分别设 1 / 2 / 5 秒，loops 先用 10；每档预期样本数为 threads × (1 + 6 × loops)。这是封闭用户模型，线程数不是每秒请求数。

| 指标 | 应如何读 |
|---|---|
| 线程数 / 并发用户 | 活跃线程，不等于始终同时在飞的请求数 |
| 吞吐量 | 本轮完成的样本数/时间，注意报告时间单位与是否含登录 |
| P50/P95/P99 | 按 sampler label 分析；P95 不是平均数，也不是“95% 成功率” |
| 错误率 | 统计 HTTP、解析与断言失败；预期 404 不能误计为业务失败 |
| elapsed / latency / connect | 总响应时间、首响应延迟、连接耗时，不能混称服务端处理时间 |
| CPU / 内存 / 磁盘 / 锁等待 | 与相同时间窗口的请求结果一起看，不能仅凭慢就认定数据库瓶颈 |

小样本百分位很不稳定。先通过短功能运行，再做有足够样本的多轮测量，记录预热是否纳入统计；不同线程档位保持其余条件一致。工具不能单凭 JTL 自动证明原因，需要服务端证据和进一步对照实验。

## 5. 报告与清理

报告填写：目标、硬件/OS/Java/JMeter/代码版本、数据规模、线程/爬升/轮次/思考时间、业务比例、样本数、各接口 P95 与错误率、资源观测、异常证据、结论与限制。模板见 `performance/REPORT_TEMPLATE.md`。

计划正常完成时每轮删除自己创建的数据；失败停止线程时可能留有任务，所以应使用专用数据库，并根据 run_id 核对残留。不能用删除共享库全部任务作为清理方案。响应正文和 token 不写入测试报告；诊断临时保存的材料也要检查。

验收：提交 JMX、至少一次全绿 JTL、至少一次断言失败被检查器拦截的记录和一份对照报告。没有真实做过测量，就不要在简历中写 QPS 或性能提升百分比。
