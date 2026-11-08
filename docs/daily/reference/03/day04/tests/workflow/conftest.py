@pytest.fixture
def task_factory(alice_client, bob_client):
    # 两个客户端都作为依赖，保证清理发生在任一 session 关闭之前。
    created = []

    def create(title=None, client=None):
        owner_client = client if client is not None else alice_client
        task = owner_client.post_json("/tasks", {"title": title if title is not None else f"case-{uuid4().hex}"})
        # 在调用方断言之前登记，后续失败也能进入清理。
        created.append((owner_client, task["id"]))
        return task

    yield create
    errors = []
    for client, task_id in reversed(created):
        try:
            client.delete(f"/tasks/{task_id}", expect_status=(204, 404))
            assert client.get_json(f"/tasks/{task_id}", expect_status=404) == {"error": "not_found"}
            print("cleanup verified", task_id)
        except Exception as exc:
            errors.append(f"task {task_id}: {exc}")
    if errors:
        pytest.fail("资源清理失败: " + "; ".join(errors))
