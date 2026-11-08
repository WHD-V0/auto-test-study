# 阶段四：用 SQL 提供可核对的数据证据

[每日目录](README.md) · [上一阶段](03-workflow.md) · [下一阶段](05-client-mock.md) · [SQL 讲解](../SQL.md) · [练习 05](../../exercises/exercise_05_sql.md)

本周使用两类数据库：`reports/learning/sql-01.sqlite3` 是三表训练库；workflow 的 `local_api_db` 是服务实际使用的单 tasks 表临时库。不要混用。自写查询放 `sql/queries/my_*.sql`，每个文件一条 SELECT；工具启动时会识别新增文件名，运行 `--name my_xxx` 不带 `.sql`。结果与解释写 `docs/sql_practice.md`。

<a id="day-1"></a>

## 第 1 天：建训练库，独立写 SELECT 与 WHERE

**材料：** `sql/seed.sql`，[SQL 讲解](../SQL.md) 第 1 节。

**操作：**

1. 初始化新库：

```powershell
.\.venv\Scripts\python.exe -m tools.sql_lab init --db reports/learning/sql-01.sqlite3
```

2. 从 seed 文件画 users、tasks、task_events 关联：谁是一对多，哪个字段关联。先写预期：3 用户、3 任务、4 事件。
3. 自写 `my_all_tasks.sql`：查询 id/title/owner/status，按 id 升序。自写 `my_alice_tasks.sql`：只查 Alice，按 id 降序。
4. 运行自己写的查询：

```powershell
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_all_tasks
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_alice_tasks
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

每个 .sql 文件是一条可被 tools.sql_lab 识别的查询。先初始化全新训练库，再执行查询；完整 SELECT 字段便于明确比较结果。以下输出是预期，不是替你执行的记录。

文件 `sql/queries/my_all_tasks.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day01/sql/queries/my_all_tasks.sql)

```sql
SELECT id, title, owner, status FROM tasks ORDER BY id ASC;
```

文件 `sql/queries/my_alice_tasks.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day01/sql/queries/my_alice_tasks.sql)

```sql
SELECT id, title, owner, status FROM tasks WHERE owner='alice' ORDER BY id DESC;
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m tools.sql_lab init --db reports/learning/sql-01.sqlite3
.\.venv\Scripts\python.exe -B -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_alice_tasks
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_all_tasks
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_alice_tasks
```

**对照运行后的结果：** my_all_tasks 的 ID 顺序为101/102/201；my_alice_tasks 为102/101。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 两个独立 SQL 文件，结果分别是 101/102/201、102/101；预期在运行前写好。
- [ ] 能指出 WHERE 筛选行、ORDER BY 决定顺序，解释 ASC/DESC。
- [ ] 画出的关系包括无任务用户 Charlie。

**卡住时：** 已存在文件会拒绝覆盖；重做用新路径，并同步后续命令，不删除已有成果。找不到新查询时核对它是否在 `sql/queries/`。

<a id="day-2"></a>

## 第 2 天：LIKE、IN、NULL 与空字符串

**材料：** `sql/queries/missing_notes.sql`，seed 中 task 101、102、201 的 note。

**操作：**

1. 自写 `my_title_like.sql`：title 以 `sql-alice-` 开头，预期 101/102。
2. 自写 `my_status_in.sql`：status IN open/done 且 owner=bob，预期仅 201；注意 AND/OR 的括号与优先级。
3. 自写 `my_null_note.sql`：`note IS NULL`，预期仅 101。临时改成 `note = ''` 应仅 102；改成 `note = NULL` 观察为何没有匹配，再恢复 IS NULL。
4. 使用昨天的 query 命令逐一替换 `--name` 为上面三个文件名，不改工具源码。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

三份是不同的筛选目标。NULL 不是空字符串；把 IS NULL 临时替换成 ='' 会选中102，而 =NULL 不会匹配任何一行。

文件 `sql/queries/my_title_like.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day02/sql/queries/my_title_like.sql)

```sql
SELECT id, title FROM tasks WHERE title LIKE 'sql-alice-%' ORDER BY id;
```

文件 `sql/queries/my_status_in.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day02/sql/queries/my_status_in.sql)

```sql
SELECT id, status FROM tasks WHERE status IN ('open','done') AND owner='bob' ORDER BY id;
```

文件 `sql/queries/my_null_note.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day02/sql/queries/my_null_note.sql)

```sql
SELECT id, note FROM tasks WHERE note IS NULL ORDER BY id;
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_null_note
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_title_like
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_status_in
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_null_note
```

**对照运行后的结果：** LIKE选中101/102；IN加owner选中201；IS NULL只选中101。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 累计五条自写查询；能不运行先预测三个结果。
- [ ] NULL、空字符串、普通文本三种值已区分，有对照结果。
- [ ] 口头解释为何判断 NULL 用 IS NULL。

**卡住时：** SQL 字符串使用单引号；`LIKE` 的 `%` 表示任意长度字符，不是 Python 格式化。

<a id="day-3"></a>

## 第 3 天：JOIN 与零任务用户

**材料：** `users_without_tasks.sql`、`event_details.sql`，SQL 讲解中 LEFT JOIN 示例。

**操作：**

1. 自写 `my_user_counts.sql`：users LEFT JOIN tasks，按 username 分组，使用 `COUNT(t.id)`，包含没有任务的用户。
2. 自写 `my_event_details.sql`：tasks JOIN task_events，展示 task_id/title/event/actor，按事件 id 排序，预期四行。
3. 第一条临时把 COUNT(t.id) 换成 COUNT(*)，记录 Charlie 从 0 变成 1 的原因，再恢复。
4. 第二条标出 task 102 出现两次，解释这不是 tasks 表真的有两条 102。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_user_counts
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_event_details
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

COUNT(t.id) 不计入 LEFT JOIN 补出的 NULL 任务，因此 Charlie 为0。事件查询的每行代表事件，任务102出现两次是正常的一对多展开。

文件 `sql/queries/my_user_counts.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day03/sql/queries/my_user_counts.sql)

```sql
SELECT u.username, COUNT(t.id) AS task_count
FROM users AS u LEFT JOIN tasks AS t ON t.owner=u.username
GROUP BY u.username ORDER BY u.username;
```

文件 `sql/queries/my_event_details.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day03/sql/queries/my_event_details.sql)

```sql
SELECT t.id AS task_id, t.title, e.event, e.actor
FROM tasks AS t JOIN task_events AS e ON e.task_id=t.id
ORDER BY e.id;
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_user_counts
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_user_counts
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_event_details
```

**对照运行后的结果：** alice=2、bob=1、charlie=0；事件明细4行。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 累计七条自写查询；用户任务数 alice=2、bob=1、charlie=0。
- [ ] 能解释 LEFT JOIN 保留什么，INNER JOIN 会遗漏谁。
- [ ] 四条事件与三个任务的数量关系说得清楚。

**卡住时：** 聚合前先输出 JOIN 明细，确认每行代表任务还是事件，再选择 COUNT 字段。

<a id="day-4"></a>

## 第 4 天：GROUP BY/HAVING 与重复计数

**材料：** `duplicates.sql`，昨天的事件明细。

**操作：**

1. 自写第八条 `my_busy_users.sql`：按 owner 分组统计任务数，HAVING 任务数至少 2，预期只有 alice=2。
2. 再写一条实验查询，把 tasks 与 task_events JOIN 后按 owner 数任务，观察 Alice 被数为 3；用 `COUNT(DISTINCT t.id)` 修正为 2。
3. 运行现有 `duplicates`，预期空数组；说明“无重复”也是有业务意义的结果，并写出它按哪些字段判断重复。
4. 把至少八条自写 SQL、每条预期行数与关键字段结果汇总到 `docs/sql_practice.md`。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_busy_users
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name duplicates
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

第八条主查询与重复计数实验分开存放，避免错误样例被误当成正确答案。DISTINCT 只解决本例“按任务计数”的粒度问题，不能不分目标到处添加。

文件 `sql/queries/my_busy_users.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day04/sql/queries/my_busy_users.sql)

```sql
SELECT owner, COUNT(*) AS task_count FROM tasks
GROUP BY owner HAVING COUNT(*) >= 2 ORDER BY owner;
```

文件 `sql/queries/my_event_counts_wrong.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day04/sql/queries/my_event_counts_wrong.sql)

故意错误的任务计数口径，用于与下一个文件比较，不作为正确业务查询。

```sql
SELECT t.owner, COUNT(t.id) AS task_count
FROM tasks AS t JOIN task_events AS e ON e.task_id=t.id
GROUP BY t.owner ORDER BY t.owner;
```

文件 `sql/queries/my_event_counts_fixed.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day04/sql/queries/my_event_counts_fixed.sql)

```sql
SELECT t.owner, COUNT(DISTINCT t.id) AS task_count
FROM tasks AS t JOIN task_events AS e ON e.task_id=t.id
GROUP BY t.owner ORDER BY t.owner;
```

文件 `docs/sql_practice.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day04/docs/sql_practice.md)

```markdown
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
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_busy_users
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_busy_users
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_event_counts_wrong
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_event_counts_fixed
```

**对照运行后的结果：** my_busy_users仅alice=2；错误/修正计数分别为alice3/alice2。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 八条独立查询已实际执行，包含 WHERE、LIKE、IN、NULL、JOIN、GROUP BY/HAVING。
- [ ] 给出重复计数的错误/修正结果，并解释 DISTINCT 的使用理由。
- [ ] 能说明 WHERE 过滤原始行、HAVING 过滤聚合组。

**卡住时：** 不要直接背 COUNT(DISTINCT)；先说清要数的是用户、任务还是事件。

<a id="day-5"></a>

## 第 5 天：事务回滚与索引执行计划

**材料：** `sql/transactions.sql`，[SQL 讲解](../SQL.md) 第 4—5 节。

**操作：** 新建 `exercises/sql_transaction_practice.py`，输入并逐句解释下面代码；只连接专用训练库：

```python
from contextlib import closing
import sqlite3

with closing(sqlite3.connect("reports/learning/sql-01.sqlite3")) as db:
    db.execute("PRAGMA foreign_keys=ON")
    statement = "SELECT id FROM tasks WHERE owner='alice' AND status='open'"
    print("before index:", db.execute("EXPLAIN QUERY PLAN " + statement).fetchall())
    db.execute("BEGIN")
    try:
        db.execute("UPDATE tasks SET status=? WHERE id=?", ("done", 101))
        assert db.execute("SELECT status FROM tasks WHERE id=101").fetchone() == ("done",)
        db.execute("CREATE INDEX idx_practice_owner_status ON tasks(owner,status)")
        print("with index:", db.execute("EXPLAIN QUERY PLAN " + statement).fetchall())
    finally:
        db.rollback()
    assert db.execute("SELECT status FROM tasks WHERE id=101").fetchone() == ("open",)
    print("rollback verified")
```

```powershell
.\.venv\Scripts\python.exe exercises/sql_transaction_practice.py
```

记录索引前后计划是否出现 SCAN/SEARCH、使用哪个索引；实际文字随 SQLite 版本可不同。再在记录中写出如果将 rollback 换为 commit，数据和索引会怎样；不必真的提交更改。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

BEGIN内更新与建索引，finally回滚两者，允许在同一训练库重复实验。占位符用于业务值，EXPLAIN拼接的是代码中固定的SELECT，不包含用户输入。

文件 `exercises/sql_transaction_practice.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day05/exercises/sql_transaction_practice.py)

```python
from contextlib import closing
import sqlite3

with closing(sqlite3.connect("reports/learning/sql-01.sqlite3")) as db:
    db.execute("PRAGMA foreign_keys=ON")
    query = "SELECT id FROM tasks WHERE owner='alice' AND status='open'"
    print("before index:", db.execute("EXPLAIN QUERY PLAN " + query).fetchall())
    db.execute("BEGIN")
    try:
        db.execute("UPDATE tasks SET status=? WHERE id=?", ("done", 101))
        assert db.execute("SELECT status FROM tasks WHERE id=101").fetchone() == ("done",)
        db.execute("CREATE INDEX idx_practice_owner_status ON tasks(owner,status)")
        print("with index:", db.execute("EXPLAIN QUERY PLAN " + query).fetchall())
    finally:
        db.rollback()
    assert db.execute("SELECT status FROM tasks WHERE id=101").fetchone() == ("open",)
    print("rollback verified")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.sql_transaction_practice
```

**对照运行后的结果：** 事务内done、回滚后open；通常从SCAN变为使用索引的SEARCH，具体文字随版本变化。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 事务内 done、回滚后 open，保存真实执行结果。
- [ ] 记录执行计划差异；能解释三行数据不能证明索引带来可测性能提升。
- [ ] 能说明 `closing` 负责关闭、rollback 负责回滚，二者不是同一件事。

**卡住时：** 如果任务 101 初值已被自己改过，先查清原因，再换新训练库初始化重做，不对服务库执行这段写操作。

<a id="day-6"></a>

## 第 6 天：给接口补一个只读落库断言

**材料：** `tests/workflow/test_database_checks.py`、`local_api_db` fixture。

**操作：**

1. 先跑现有落库样例，读懂 `mode=ro`、`?` 参数绑定、owner 条件。
2. 在 `tests/workflow/test_database_extended.py` 自写场景：工厂建任务 → HTTP 删除 204 → HTTP 查询 404 → 用 `local_api_db` 只读查同 ID/owner，应为 None。
3. 再自写非法更新原子性场景：before/open → 合法 title 加非法 status → 400 → HTTP 原值不变 → SQL 也为原值。可复用样例的 `read_task`，但断言自己写。
4. 不能用 SQL 准备业务资源或连手动服务的固定库；资源仍由 API 建立和清理。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_database_checks.py -v
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_database_extended.py -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

两条测试完整提供了HTTP与SQL核对。SQL只能读fixture给的local_api_db，不能拿训练库路径替代。closing关闭连接，mode=ro禁止这里偷偷写业务数据。

文件 `tests/workflow/test_database_extended.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day06/tests/workflow/test_database_extended.py)

```python
from contextlib import closing
import sqlite3


def read_task(db_path, task_id):
    uri = db_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        return db.execute("SELECT title,status,owner FROM tasks WHERE id=? AND owner=?",
                          (task_id, "alice")).fetchone()


def test_delete_is_persisted(alice_client, task_factory, local_api_db):
    task = task_factory("delete-check")
    path = f"/tasks/{task['id']}"
    assert read_task(local_api_db, task["id"]) == ("delete-check", "open", "alice")
    assert alice_client.delete(path, expect_status=204).content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}
    assert read_task(local_api_db, task["id"]) is None


def test_invalid_update_keeps_database_unchanged(alice_client, task_factory, local_api_db):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "after", "status": "bad"}, expect_status=400)
    assert alice_client.get_json(path) == task
    assert read_task(local_api_db, task["id"]) == ("before", "open", "alice")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_database_extended.py -q
```

**对照运行后的结果：** 2 passed；删除后无行、非法更新后title/status/owner完全不变。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 至少一个自写测试包含参数绑定和只读连接，本教程的两个场景均完成更好。
- [ ] HTTP 与 SQL 的预期一致；非法更新没有部分写入。
- [ ] 能说明训练三表库与服务单表库区别，以及为什么不能拿训练库验证 API。

**卡住时：** sqlite3 的 `fetchone()` 返回 tuple 或 None，不能直接按 JSON 字典比较。

<a id="day-7"></a>

## 第 7 天：闭卷查询、并行回归与 SQL 交付

**操作：**

1. 合上查询样例，另写一条“所有 qa 部门用户及任务数量，包含零任务用户”的查询，预期 alice=2、charlie=0；现场再把 qa 改为 dev，预期 bob=1。
2. 运行自己的落库文件与完整 workflow 并行回归。
3. 整理 `docs/sql_practice.md`、八条查询、事务/计划输出、测试 nodeid；列出 MySQL 迁移时需重新验证的占位符、事务/隔离、排序规则、EXPLAIN 差异。

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_database_extended.py -n 2
.\.venv\Scripts\python.exe -m pytest tests/workflow -n 2
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

闭卷题的WHERE筛选的是users部门，因此Charlie仍被LEFT JOIN保留。检查脚本把预期写成可执行断言，只校验专用种子数据；真实项目数据变化时不能照搬这些固定ID。

文件 `sql/queries/my_department_counts.sql` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day07/sql/queries/my_department_counts.sql)

```sql
SELECT u.username, COUNT(t.id) AS task_count
FROM users AS u LEFT JOIN tasks AS t ON t.owner=u.username
WHERE u.department='qa' GROUP BY u.username ORDER BY u.username;
```

文件 `exercises/check_sql_answers.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/04/day07/exercises/check_sql_answers.py)

```python
from pathlib import Path
from tools.sql_lab import query

database = Path("reports/learning/sql-01.sqlite3")
expected_ids = {
    "my_all_tasks": [101, 102, 201], "my_alice_tasks": [102, 101],
    "my_title_like": [101, 102], "my_status_in": [201], "my_null_note": [101],
}
for name, expected in expected_ids.items():
    actual = [row["id"] for row in query(database, name)]
    assert actual == expected, (name, actual)
assert query(database, "my_user_counts") == [
    {"username": "alice", "task_count": 2}, {"username": "bob", "task_count": 1},
    {"username": "charlie", "task_count": 0}]
assert len(query(database, "my_event_details")) == 4
assert query(database, "my_busy_users") == [{"owner": "alice", "task_count": 2}]
assert query(database, "my_department_counts") == [
    {"username": "alice", "task_count": 2}, {"username": "charlie", "task_count": 0}]
print("8条主查询及部门闭卷题：预期全部匹配")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.check_sql_answers
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_database_extended.py -n 2 -q
.\.venv\Scripts\python.exe -m tools.sql_lab query --db reports/learning/sql-01.sqlite3 --name my_department_counts
```

**对照运行后的结果：** 查询脚本退出0；自己的两个落库测试双worker通过。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 闭卷 SQL 及改变条件后的输出正确，解释每个 JOIN/聚合字段。
- [ ] 练习 05 的查询、事务、计划、至少一个落库测试均有证据。
- [ ] 只声明已做过的 SQLite 练习，不把 MySQL 迁移知识清单当成实操经历。

**未通过怎么办：** NULL 回第 2 天；计数回第 3—4 天；事务/计划回第 5 天；库路径混乱回第 6 天。
