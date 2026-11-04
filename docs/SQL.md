# SQL：用数据证据验证接口

对应阶段四、练习 05。目标是独立查询和核对业务数据，理解事务与索引对测试的影响。这里使用 Python 自带 SQLite，避免安装数据库成为学习门槛；MySQL 是迁移练习，完成 SQLite 不能写成“熟练使用 MySQL”。

## 1. 准备一个可重复的数据集

下面的 python 指虚拟环境解释器；PowerShell 可写 `.\.venv\Scripts\python.exe`。所有命令在项目根目录运行。

```text
python -m tools.sql_lab init --db reports/sql-lab.sqlite3
python -m tools.sql_lab query --db reports/sql-lab.sqlite3 --name task_counts
```

初始化只创建新文件，遇到已有文件会拒绝覆盖。重做请换路径，例如 reports/sql-lab-02.sqlite3。这个训练库与服务使用的 tasks.sqlite3 是两个独立数据库，不要混用。

数据来自 `sql/seed.sql`：users 有 alice/bob/charlie 三个用户；tasks 有 Alice 的 open/done 各一条和 Bob 的 open 一条；task_events 有四条事件。Charlie 没有任务，Alice 有一条任务的 note 为 NULL、一条为空串。

## 2. 测试中优先掌握的 SQL

| 能力 | 解决的问题 | 动手材料 |
|---|---|---|
| SELECT、WHERE、AND/OR、ORDER BY | 精确找到本次测试创建的数据 | open_tasks.sql |
| LIKE、IN、IS NULL | 前缀检索、状态筛选、区分空值与空字符串 | missing_notes.sql |
| COUNT、SUM、GROUP BY、HAVING | 数量核对、汇总、重复业务数据排查 | task_counts.sql、duplicates.sql |
| INNER JOIN、LEFT JOIN | 核对关联表，找到没有任务的用户 | event_details.sql、users_without_tasks.sql |
| BEGIN、COMMIT、ROLLBACK | 验证整体成功或整体失败，避免部分写入 | transactions.sql |
| 参数绑定 | 根据接口返回 ID 查数据，避免拼接 SQL | tests/workflow/test_database_checks.py |
| EXPLAIN 与索引基础 | 判断查询为什么扫描多行，提出验证方案 | 本章第 5 节 |

示例：每位用户的任务数，包括零任务用户。

```sql
SELECT u.username, COUNT(t.id) AS task_count
FROM users AS u
LEFT JOIN tasks AS t ON t.owner = u.username
GROUP BY u.username
ORDER BY u.username;
```

预期 alice=2、bob=1、charlie=0。这里不能换成 COUNT(*)：LEFT JOIN 为无任务用户保留的一行也会被它计数。不要把一对多事件表 JOIN 进来后直接 COUNT(task.id)，否则同一个任务可能被重复计算；先聚合、COUNT(DISTINCT ...) 或选对查询粒度。

```text
python -m tools.sql_lab query --db reports/sql-lab.sqlite3 --name users_without_tasks
python -m tools.sql_lab query --db reports/sql-lab.sqlite3 --name event_details
python -m tools.sql_lab query --db reports/sql-lab.sqlite3 --name duplicates
python -m tools.sql_lab query --db reports/sql-lab.sqlite3 --name missing_notes
```

所有 query 子命令用只读连接。预期：无任务用户只有 charlie；事件明细 4 行；重复任务为空；缺少备注的任务只有 101（102 的空字符串不是 NULL）。完整查询见 `sql/queries/`，每个文件一条 SELECT。

## 3. 把 SQL 接到接口测试后面

阅读 `tests/workflow/test_database_checks.py`：资源仍通过 API 创建/修改；再根据返回的 id 和当前 owner，用只读数据库连接查询，核对落库值。新增数据库路径 fixture 仍然每个 worker 一份，禁止读取手动启动服务的共享数据库。

```python
from contextlib import closing
import sqlite3

# db_path 是 fixture 提供的 Path；不拼接业务参数进 SQL。
with closing(sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
    row = db.execute(
        'SELECT title, status FROM tasks WHERE id=? AND owner=?',
        (task_id, 'alice'),
    ).fetchone()
assert row == ('changed', 'done')
```

数据库核对用于发现错误落库、部分更新等问题；公开接口契约仍应通过 HTTP 断言验证。不是每个测试都需要查库，也不能为了断言直接修改业务库。实际服务若异步写入，应按约定轮询并设置超时预算，不能随意 sleep 后假设数据已一致。

## 4. 事务实验

`sql/transactions.sql` 在专用训练库内执行更新、查询再回滚；用 sqlite3 CLI 的 `.read` 运行（未安装 CLI 时看文件里的 Python 等价步骤）。运行前后 task 101 都应为 open。

理解：COMMIT 才提交；ROLLBACK 撤销当前未提交事务；SQLite 连接的 with 处理事务，不自动 close，所以示例使用 closing。训练库开启外键约束需要每个写连接设置 PRAGMA foreign_keys=ON。服务本身仅有 tasks 表，不能根据训练库结构推断服务具有用户表或审计表。

## 5. 索引与迁移边界

只在训练库尝试：

```sql
EXPLAIN QUERY PLAN SELECT id FROM tasks WHERE owner='alice' AND status='open';
BEGIN;
CREATE INDEX idx_tasks_owner_status ON tasks(owner, status);
EXPLAIN QUERY PLAN SELECT id FROM tasks WHERE owner='alice' AND status='open';
ROLLBACK;
```

比较执行计划中的 SCAN/SEARCH；三行数据不足以证明性能提升，索引还会增加写入和存储成本。去掉 WHERE 的 UPDATE/DELETE 会影响整张表，练习限定训练库并先 SELECT 确认范围。

迁移 MySQL 时重新验证：连接驱动与 `%s` 占位符、AUTO_INCREMENT、事务与隔离级别、外键/唯一约束、NULL、排序规则、EXPLAIN 格式。SQLite 的 `?`、PRAGMA 和 `EXPLAIN QUERY PLAN` 不能原样当作 MySQL 用法。

验收：独立写出至少 8 条有业务含义的查询，说明预期行数；完成 LEFT JOIN、NULL、重复数据和事务实验；新增至少一个参数绑定的接口落库断言。提交 SQL 文件、查询结果和异常数据说明。
