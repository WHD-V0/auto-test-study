-- 独立教学数据集，不是任务 API 的实际表结构。
PRAGMA foreign_keys = ON;
BEGIN;
CREATE TABLE users (username TEXT PRIMARY KEY, department TEXT NOT NULL);
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open', 'done')),
    owner TEXT NOT NULL REFERENCES users(username),
    note TEXT
);
CREATE TABLE task_events (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    event TEXT NOT NULL,
    actor TEXT NOT NULL REFERENCES users(username)
);
INSERT INTO users VALUES ('alice', 'qa'), ('bob', 'dev'), ('charlie', 'qa');
INSERT INTO tasks VALUES
    (101, 'sql-alice-open', 'open', 'alice', NULL),
    (102, 'sql-alice-done', 'done', 'alice', ''),
    (201, 'sql-bob-open', 'open', 'bob', 'needs review');
INSERT INTO task_events VALUES
    (1, 101, 'created', 'alice'), (2, 102, 'created', 'alice'),
    (3, 102, 'completed', 'alice'), (4, 201, 'created', 'bob');
COMMIT;
