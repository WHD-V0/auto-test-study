SELECT owner, COUNT(*) AS task_count FROM tasks
GROUP BY owner HAVING COUNT(*) >= 2 ORDER BY owner;
