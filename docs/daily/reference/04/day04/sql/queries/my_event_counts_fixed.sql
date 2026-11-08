SELECT t.owner, COUNT(DISTINCT t.id) AS task_count
FROM tasks AS t JOIN task_events AS e ON e.task_id=t.id
GROUP BY t.owner ORDER BY t.owner;
