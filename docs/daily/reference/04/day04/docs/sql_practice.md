# SQL 作业参考说明

| 文件 | 预期 | 含义 |
|---|---|---|
| my_all_tasks | 101/102/201 | 全部任务，ID升序 |
| my_alice_tasks | 102/101 | Alice任务，ID降序 |
| my_title_like | 101/102 | 标题前缀匹配 |
| my_status_in | 201 | 状态集合与Bob条件同时成立 |
| my_null_note | 101 | NULL不是102的空字符串 |
| my_user_counts | alice2/bob1/charlie0 | LEFT JOIN保留零任务用户 |
| my_event_details | 4行 | 粒度为事件，102重复出现 |
| my_busy_users | alice2 | HAVING筛选聚合后的计数 |

错误的事件JOIN计数：Alice=3；COUNT(DISTINCT t.id)后Alice=2。
WHERE先筛行，GROUP BY分组，HAVING筛组，ORDER BY确定顺序。
以上是预期对照，实际日期、查询输出、事务和执行计划由本人运行后附上。
