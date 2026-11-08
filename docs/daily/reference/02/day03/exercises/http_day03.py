from exercises.manual_http import BASE, login, checked

cases = [
    ("one", "x", 201), ("max", "x" * 80, 201), ("too-long", "x" * 81, 400),
    ("blank", "   ", 400), ("number", 123, 400), ("trim", "  hello  ", 201),
]
with login() as session:
    for name, title, expected in cases:
        before = checked(session, "GET", "/tasks", 200).json()
        task_id = None
        try:
            response = checked(session, "POST", "/tasks", expected, json={"title": title})
            if expected == 201:
                task = response.json()
                task_id = task["id"]
                assert task["title"] == title.strip()
                assert checked(session, "GET", f"/tasks/{task_id}", 200).json() == task
            else:
                assert response.json() == {"error": "invalid_fields"}
                assert checked(session, "GET", "/tasks", 200).json() == before
            print(name, expected, "PASS")
        finally:
            if task_id is not None:
                assert session.delete(f"{BASE}/tasks/{task_id}", timeout=3).status_code in (204, 404)
