# 练习 05：SQL 与接口数据核对

每天怎么做：[阶段四逐日教程](../docs/daily/04-sql.md)，含自写查询的预期结果、事务命令、落库测试与每日验收。

材料：[SQL 章节](../docs/SQL.md)、sql/seed.sql、sql/queries/、tests/workflow/test_database_checks.py。

1. 用新路径初始化训练库，先画 users/tasks/task_events 的关系。
2. 独立写至少 8 条查询，涵盖 WHERE、LIKE、IN、IS NULL、JOIN、GROUP BY/HAVING，逐条说明预期结果。
3. 查询所有用户任务数（包括 0），解释 COUNT(*) 与 COUNT(t.id) 差异；用事件表说明一对多重复计数。
4. 在专用训练库做更新→事务内查询→回滚→再查询，保留结果。
5. 比较索引前后执行计划，说明为什么三行数据不能证明性能提升。
6. 给一个接口场景增加只读落库断言，使用 fixture 的 worker 数据库和参数绑定，不拼接用户输入。

交付：docs/sql_practice.md、独立 SQL 文件、查询结果和新增测试。验收：能现场修改筛选条件并解释输出；不把 SQLite 操作当作已掌握 MySQL 实战。
