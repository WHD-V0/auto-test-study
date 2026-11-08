SELECT id, status FROM tasks WHERE status IN ('open','done') AND owner='bob' ORDER BY id;
