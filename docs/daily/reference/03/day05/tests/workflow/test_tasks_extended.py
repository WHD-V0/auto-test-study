@pytest.mark.parametrize("title", ["x", "x" * 80, "  normalized  "], ids=["min", "max", "trim"])
def test_title_boundaries(alice_client, task_factory, title):
    task = task_factory(title)
    assert task["title"] == title.strip()
    assert_schema(task, TASK_SCHEMA)
    assert alice_client.get_json(f"/tasks/{task['id']}") == task


@pytest.mark.parametrize("title", ["x" * 81, "   ", None, 123], ids=["too-long", "blank", "null", "number"])
def test_title_invalid(alice_client, title):
    before = alice_client.get_json("/tasks")
    result = alice_client.post_json("/tasks", {"title": title}, expect_status=400)
    assert result == {"error": "invalid_fields"}
    assert alice_client.get_json("/tasks") == before


def test_invalid_update_is_atomic_extended(alice_client, task_factory):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    result = alice_client.put_json(path, {"title": "changed", "status": "unknown"}, expect_status=400)
    assert result == {"error": "invalid_fields"}
    assert alice_client.get_json(path) == task


@pytest.mark.parametrize("field,value", [("owner", "bob"), ("id", 9)])
def test_unknown_fields_extended(alice_client, field, value):
    before = alice_client.get_json("/tasks")
    alice_client.post_json("/tasks", {"title": "protected", field: value}, expect_status=400)
    assert alice_client.get_json("/tasks") == before


def test_invalid_json_extended(alice_client):
    before = alice_client.get_json("/tasks")
    response = alice_client.request("POST", "/tasks", data="{",
        headers={"Content-Type": "application/json"}, expect_status=400)
    assert response.json() == {"error": "invalid_json_object"}
    assert alice_client.get_json("/health") == {"status": "ok"}
    assert alice_client.get_json("/tasks") == before
