from pathlib import Path
from tools.sql_lab import query

database = Path("reports/learning/sql-01.sqlite3")
expected_ids = {
    "my_all_tasks": [101, 102, 201], "my_alice_tasks": [102, 101],
    "my_title_like": [101, 102], "my_status_in": [201], "my_null_note": [101],
}
for name, expected in expected_ids.items():
    actual = [row["id"] for row in query(database, name)]
    assert actual == expected, (name, actual)
assert query(database, "my_user_counts") == [
    {"username": "alice", "task_count": 2}, {"username": "bob", "task_count": 1},
    {"username": "charlie", "task_count": 0}]
assert len(query(database, "my_event_details")) == 4
assert query(database, "my_busy_users") == [{"owner": "alice", "task_count": 2}]
assert query(database, "my_department_counts") == [
    {"username": "alice", "task_count": 2}, {"username": "charlie", "task_count": 0}]
print("8条主查询及部门闭卷题：预期全部匹配")
