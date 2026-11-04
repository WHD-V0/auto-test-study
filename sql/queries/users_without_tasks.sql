SELECT u.username
FROM users AS u
LEFT JOIN tasks AS t ON t.owner = u.username
WHERE t.id IS NULL
ORDER BY u.username;
