"""需求驱动的本地 HTTP 集成测试；不读取服务端数据库来代替业务断言。"""
import pytest

from core.validator import assert_schema

pytestmark = pytest.mark.integration

TASK_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "status", "owner"],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1, "maxLength": 80},
        "status": {"enum": ["open", "done"]},
        "owner": {"type": "string"},
    },
}


@pytest.mark.smoke
def test_full_crud(alice_client, task_factory):
    """TASK-01：同一个 ID 的持久化闭环，而不是几个无关请求。"""
    created = task_factory("first")
    assert_schema(created, TASK_SCHEMA)
    assert created["owner"] == "alice"
    assert created["status"] == "open"
    path = f"/tasks/{created['id']}"
    assert alice_client.get_json(path) == created
    updated = alice_client.put_json(path, {"title": "changed", "status": "done"})
    assert updated == {**created, "title": "changed", "status": "done"}
    assert alice_client.get_json(path) == updated
    deleted = alice_client.delete(path, expect_status=204)
    assert deleted.content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}
    alice_client.delete(path, expect_status=404)


@pytest.mark.parametrize("token", [None, "not-a-valid-token"], ids=["missing", "invalid"])
def test_authentication_required(anonymous_client, token, alice_client):
    """TASK-02/03：拒绝写入，也不产生新任务。"""
    before = alice_client.get_json("/tasks")
    if token:
        anonymous_client.set_token(token)
    result = anonymous_client.post_json("/tasks", {"title": "must-not-exist"}, expect_status=401)
    assert result == {"error": "unauthorized"}
    assert alice_client.get_json("/tasks") == before


def test_invalid_login(anonymous_client):
    result = anonymous_client.post_json("/login", {"username": "alice", "password": "wrong"}, expect_status=401)
    assert result == {"error": "invalid_credentials"}


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_other_user_cannot_access_task(method, alice_client, bob_client, task_factory):
    """TASK-04：携带另一个合法用户的 token，也必须拒绝越权。"""
    task = task_factory()
    path = f"/tasks/{task['id']}"
    kwargs = {"json": {"title": "stolen"}} if method == "PUT" else {}
    response = bob_client.request(method, path, expect_status=403, **kwargs)
    assert response.json() == {"error": "forbidden"}
    assert alice_client.get_json(path) == task


def test_list_is_scoped_to_current_user(alice_client, bob_client, task_factory):
    alice_task = task_factory()
    bob_task = task_factory(client=bob_client)
    for client, username, own, other in [
        (alice_client, "alice", alice_task, bob_task),
        (bob_client, "bob", bob_task, alice_task),
    ]:
        items = client.get_json("/tasks")["items"]
        assert_schema(items, {"type": "array", "items": TASK_SCHEMA})
        assert own in items
        assert other["id"] not in [item["id"] for item in items]
        assert all(item["owner"] == username for item in items)


@pytest.mark.parametrize("title", ["", "   ", None, 123, [], "x" * 81],
                         ids=["empty", "blank", "null", "number", "array", "too-long"])
def test_invalid_title_does_not_create_task(alice_client, title):
    before = alice_client.get_json("/tasks")
    response = alice_client.post_json("/tasks", {"title": title}, expect_status=400)
    assert response == {"error": "invalid_fields"}
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("title", ["x", "x" * 80, "  normalized  "], ids=["min", "max", "trim"])
def test_title_boundaries_and_normalization(alice_client, task_factory, title):
    task = task_factory(title)
    assert task["title"] == title.strip()
    assert_schema(task, TASK_SCHEMA)
    assert alice_client.get_json(f"/tasks/{task['id']}") == task


@pytest.mark.parametrize("body", [
    {}, {"title": "valid", "owner": "bob"}, {"title": "valid", "id": 9},
    {"title": "valid", "status": "done"},
], ids=["missing-title", "owner-protected", "id-protected", "status-protected"])
def test_create_rejects_unknown_or_missing_fields(alice_client, body):
    before = alice_client.get_json("/tasks")
    alice_client.post_json("/tasks", body, expect_status=400)
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("body", [
    {"title": "changed", "status": "unknown"}, {"title": "changed", "status": None},
    {}, {"owner": "bob"}, {"id": 2}, {"title": " "},
], ids=["bad-status", "null-status", "empty", "owner", "id", "blank-title"])
def test_invalid_update_is_atomic(alice_client, task_factory, body):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, body, expect_status=400)
    assert alice_client.get_json(path) == task


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_missing_resource(alice_client, task_factory, method):
    task = task_factory()
    path = f"/tasks/{task['id']}"
    alice_client.delete(path, expect_status=204)
    kwargs = {"json": {"title": "changed"}} if method == "PUT" else {}
    assert alice_client.request(method, path, expect_status=404, **kwargs).json() == {"error": "not_found"}


def test_invalid_json_keeps_service_available(alice_client):
    before = alice_client.get_json("/tasks")
    response = alice_client.request("POST", "/tasks", expect_status=400,
                                    data='{', headers={"Content-Type": "application/json"})
    assert response.json() == {"error": "invalid_json_object"}
    assert response.headers["X-Request-ID"]
    assert alice_client.get_json("/health") == {"status": "ok"}
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("task_id", ["invalid", "0", "-1", "9" * 30],
                         ids=["text", "zero", "negative", "overflow"])
def test_invalid_resource_id_returns_404(alice_client, task_id):
    """非法或超出数据库整数范围的 ID，不应导致连接中断或 500。"""
    result = alice_client.get_json(f"/tasks/{task_id}", expect_status=404)
    assert result == {"error": "not_found"}
