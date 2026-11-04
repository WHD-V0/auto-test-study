SELECT e.id AS event_id, t.id AS task_id, t.title, e.event, u.department
FROM task_events AS e
INNER JOIN tasks AS t ON t.id = e.task_id
INNER JOIN users AS u ON u.username = e.actor
ORDER BY e.id;
