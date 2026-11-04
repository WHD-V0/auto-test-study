-- 仅在已初始化的专用 SQL 训练库执行。
-- sqlite3 reports/sql-lab.sqlite3
-- .read sql/transactions.sql
BEGIN;
UPDATE tasks SET status = 'done' WHERE id = 101 AND owner = 'alice';
SELECT id, status FROM tasks WHERE id = 101; -- 事务内应为 done
ROLLBACK;
SELECT id, status FROM tasks WHERE id = 101; -- 回滚后应为 open

-- 没有 sqlite3 CLI 时，在 Python 中执行以下等价流程：
-- with closing(sqlite3.connect('reports/sql-lab.sqlite3')) as db:
--     db.execute('BEGIN')
--     db.execute('UPDATE tasks SET status=? WHERE id=?', ('done', 101))
--     assert db.execute('SELECT status FROM tasks WHERE id=?', (101,)).fetchone() == ('done',)
--     db.rollback()
--     assert db.execute('SELECT status FROM tasks WHERE id=?', (101,)).fetchone() == ('open',)
