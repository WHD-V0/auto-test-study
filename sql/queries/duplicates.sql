-- 业务键以 owner/title 为例，是否真的要求唯一必须先确认需求。
SELECT owner, title, COUNT(*) AS copies
FROM tasks
GROUP BY owner, title
HAVING COUNT(*) > 1
ORDER BY owner, title;
