# 当前扩展的验证记录

日期：2026-11-04。以下是教程维护时的验证，不代表学习者已经完成个人作业。

| 内容 | 结果 | 限制 |
|---|---|---|
| Python 双进程回归 | 108 条通过，生成 HTML/JUnit | 默认不运行 10 条公共网络测试 |
| SQL 实验 | 六份查询结果、只读前后文件内容、拒绝覆盖、事务回滚及 CLI 验证通过 | SQLite 训练库；未验证 MySQL |
| 接口落库断言 | 已纳入回归 | worker 临时数据库，非共享环境 |
| Bash 脚本 | 语法通过；业务目录 37 条通过；错误路径非零退出并留日志 | 使用 Windows Git Bash；未在真实 Linux/WSL 主机运行 |
| JTL 检查器 | 构造的预期 404 成功返回 0；HTTP 200 断言失败返回 1；缺失/非法样本测试通过 | 构造 CSV 是工具测试，不是压测结果 |
| JMX | XML、组件/hashTree 配对、7 个 sampler 和关联配置已检查 | JMeter 5.6.3 目标计划尚未经过引擎实测 |
| 文档和 CI | 本地链接、Python 语法、Shell LF 与 CI YAML 结构检查通过 | GitHub Actions 尚未在远程触发 |

本机没有可用的已安装 JMeter；两次官方运行时下载过慢，已停止。因此没有生成真实 JTL、性能数据或容量结论。按 JMeter 章节准备工具后，先执行 1 线程×3 轮并校验 19 个样本，再做对照实验。发现计划与环境不兼容时记录版本、错误和最短复现，不将静态检查写成实测成功。

学习者需在自己的环境补齐 Linux、JMeter 和远程 CI 的真实记录，再按学习成果与简历章节验收。已有 pytest 报告在 reports/report.html，Bash 成功/失败演示分别在 reports/bash-validation/success 和 failure。

## 逐日教程补充验证（2026-11-08）

新增 [每日操作与验收手册](daily/README.md) 与九阶段逐日章节，README、路线和七份练习均提供入口。以下是本次维护检查，不是替学习者完成作业：

- 完整性：九个章节各七天，共 63 天；每一天都有稳定跳转锚点和至少三项完成勾选。
- 文档：检查了 README、路线、每日手册和练习中的 114 个本地链接及锚点，均有效。
- 代码块：九个逐日章节的 7 个 Python 代码块通过语法检查；51 个 PowerShell 代码块通过解析检查。语法检查不等于执行了安装、远程推送或负载命令。
- SQL：在全新临时训练库执行教程中的事务/索引示例，观察到 SCAN→SEARCH，事务内 done、回滚后 open，断言通过。
- 当前工作区默认回归：111 passed、10 deselected，含学习者新增的 3 条第一天测试；未修改学习者的该文件。测试数量会随个人练习变化，不用作个人能力评分。

本次未新增真实 Linux/WSL、JMeter 引擎或远程 GitHub Actions 实测结果。这些步骤在教程中明确要求学习者实际执行并留证，不能按静态检查直接勾选完成。

## 每日完整参考代码验证（2026-11-08）

在原操作手册中为全部 63 天补入“当天写完后的参考代码”、目标路径、写入方式、代码解释、可执行命令与预期结果。参考文件另存于 [按天索引](daily/reference/README.md)，未将答案覆盖到学习者的 src/tests。

- [参考检查器](../tools/check_daily_reference.py) 在 reports 下建立临时项目副本，按天应用追加/替换/删除，再运行测试；设计日与需要外部工具的步骤不冒充本机实测。
- 42 个学习日配置的 Python/HTTP/SQL 实验实际执行通过，包括字符串、fixture清理、重启持久化、CRUD/权限、顺序/并行、SQL、Mock、预期失败、源码恢复与归档变更。
- 49 份 Python 参考通过语法检查；16 份 PowerShell 脚本通过解析；8 份 Bash 脚本通过 Git Bash 语法检查；3 份 JMX 通过 XML、sampler数量及hashTree配对检查；1 份 CI YAML 通过结构读取。
- 321 个本地链接/锚点有效；每日文档与对应参考文件的代码内容一致。
- 指标脚本通过构造CSV的测试，校验数量、按label统计、P95及Markdown输出。构造CSV只证明脚本可用，不是JMeter运行结果或性能数据。
- PowerShell参考文件采用UTF-8带BOM，以兼容Windows PowerShell 5中的中文；Bash使用LF。

可复现命令：`python -m tools.check_daily_reference`；仅查语法/结构/链接用 `--static-only`，单阶段用 `--stage 1`。完整参考中的Linux实操、远程CI、JMeter引擎与真实负载仍需在对应环境另行执行。学习者当前未完成的作业不被此临时副本检查改写。
