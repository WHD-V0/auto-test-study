# 我的归档功能交付说明（参考结构）

个人新增：状态转换/归档锁定、列表过滤、归档HTTP和SQL测试、JMeter归档查询断言。
复用：教程的HTTP/SQLite靶场、APIClient、登录fixture、任务工厂、CI基础结构。
设计：change_archive.md及archive_cases.md；契约：API_CONTRACT.md的归档规则。
运行：python -m pytest tests/workflow/test_archive.py；python -m pytest -n 2。
演示：重启归档版手动服务后python -m exercises.archive_demo。
故障：python -m exercises.verify_archive_mutation；缺陷说明bug_report_archive.md。
SQL：归档成功status落库；409时title/status均保持原值。
清理：工厂按ID删除；JMeter残留使用include_archived=true列表按run_id过滤回收。
JMeter：my_archive_workflow.jmx，1线程3轮25样本，以JTL检查器为门槛。
限制：教学鉴权、SQLite本机同步写、短时同机实验；未证明生产容量。

本人实际代码版本/差异、Windows与Linux报告、CI链接、JTL路径、检查器退出码：执行后填写。
未完成项：据实列出；不能把参考脚本存在写成实际执行通过。
