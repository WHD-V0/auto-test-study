SELECT t.id AS task_id, t.title, e.event, e.actor
FROM tasks AS t JOIN task_events AS e ON e.task_id=t.id
ORDER BY e.id;
