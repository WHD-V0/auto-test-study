from exercises.manual_http import BASE, login, checked

with login() as session:
    task_id = None
    try:
        created = checked(session, "POST", "/tasks", 201, json={"title": "manual-day02"})
        task = created.json()
        task_id = task["id"]  # 在后面的断言前登记，失败时也可清理。
        path = f"/tasks/{task_id}"
        assert task["owner"] == "alice"
        assert task["status"] == "open"
        assert checked(session, "GET", path, 200).json() == task
        deleted = checked(session, "DELETE", path, 204)
        assert deleted.content == b""
        assert checked(session, "GET", path, 404).json() == {"error": "not_found"}
        print("201 → 200 → 204 → 404，同一资源闭环通过")
    finally:
        if task_id is not None:
            response = session.delete(f"{BASE}/tasks/{task_id}", timeout=3)
            assert response.status_code in (204, 404)
