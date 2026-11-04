SELECT id, title, status, owner
FROM tasks
WHERE owner = 'alice' AND status IN ('open') AND title LIKE 'sql-%'
ORDER BY id;
