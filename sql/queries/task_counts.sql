SELECT u.username, COUNT(t.id) AS task_count
FROM users AS u
LEFT JOIN tasks AS t ON t.owner = u.username
GROUP BY u.username
ORDER BY u.username;
