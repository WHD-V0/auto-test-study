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
