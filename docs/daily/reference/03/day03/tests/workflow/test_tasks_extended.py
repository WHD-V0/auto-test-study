def test_list_user_isolation(alice_client, bob_client, task_factory):
    alice_task = task_factory("alice-list")
    bob_task = task_factory("bob-list", client=bob_client)
    for client, owner, own, other in [
        (alice_client, "alice", alice_task, bob_task),
        (bob_client, "bob", bob_task, alice_task),
    ]:
        items = client.get_json("/tasks")["items"]
        assert_schema(items, {"type": "array", "items": TASK_SCHEMA})
        ids = [item["id"] for item in items]
        assert own["id"] in ids
        assert other["id"] not in ids
        assert all(item["owner"] == owner for item in items)
        assert ids == sorted(ids)


def test_list_excludes_deleted_task(alice_client, task_factory):
    task = task_factory("will-delete")
    alice_client.delete(f"/tasks/{task['id']}", expect_status=204)
    items = alice_client.get_json("/tasks")["items"]
    assert task["id"] not in [item["id"] for item in items]
