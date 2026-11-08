import pytest
from core.validator import assert_schema
from tests.workflow.test_tasks import TASK_SCHEMA


def make_state(alice_client, task_factory, state):
    task = task_factory("archive-case")
    path = f"/tasks/{task['id']}"
    if state in ("done", "archived"):
        task = alice_client.put_json(path, {"status": "done"})
    if state == "archived":
        task = alice_client.put_json(path, {"status": "archived"})
    return task


def test_done_to_archived_transition(alice_client, task_factory):
    task = make_state(alice_client, task_factory, "done")
    path = f"/tasks/{task['id']}"
    archived = alice_client.put_json(path, {"status": "archived"})
    assert archived == {**task, "status": "archived"}
    assert alice_client.get_json(path) == archived


def test_open_to_archived_transition_is_conflict(alice_client, task_factory):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "after", "status": "archived"}, expect_status=409)
    assert alice_client.get_json(path) == task


@pytest.mark.parametrize("before,after,expected", [
    ("open", "open", 200), ("open", "done", 200), ("done", "open", 200),
    ("done", "done", 200), ("done", "archived", 200), ("open", "archived", 409),
    ("archived", "open", 409), ("archived", "done", 409),
], ids=["open-open", "open-done", "done-open", "done-done", "done-archive", "open-archive", "archive-open", "archive-done"])
def test_transition_matrix(alice_client, task_factory, before, after, expected):
    task = make_state(alice_client, task_factory, before)
    path = f"/tasks/{task['id']}"
    result = alice_client.put_json(path, {"status": after}, expect_status=expected)
    if expected == 200:
        assert result == {**task, "status": after}
        assert_schema(result, TASK_SCHEMA)
        assert alice_client.get_json(path) == result
    else:
        assert alice_client.get_json(path) == task


def test_archived_title_is_locked(alice_client, task_factory):
    task = make_state(alice_client, task_factory, "archived")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "changed"}, expect_status=409)
    assert alice_client.get_json(path) == task


def test_archived_can_be_deleted(alice_client, task_factory):
    task = make_state(alice_client, task_factory, "archived")
    path = f"/tasks/{task['id']}"
    assert alice_client.delete(path, expect_status=204).content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}


@pytest.mark.parametrize("query", ["", "?include_archived=false"], ids=["default", "false"])
def test_default_list_excludes_archived(alice_client, task_factory, query):
    active = make_state(alice_client, task_factory, "open")
    done = make_state(alice_client, task_factory, "done")
    archived = make_state(alice_client, task_factory, "archived")
    items = alice_client.get_json("/tasks" + query)["items"]
    ids = [item["id"] for item in items]
    assert active["id"] in ids and done["id"] in ids
    assert archived["id"] not in ids
    assert all(item["status"] != "archived" for item in items)
    assert ids == sorted(ids)


def test_include_archived_lists_only_own_tasks(alice_client, bob_client, task_factory):
    own = [make_state(alice_client, task_factory, state) for state in ("open", "done", "archived")]
    other = task_factory("bob-private", client=bob_client)
    items = alice_client.get_json("/tasks?include_archived=true")["items"]
    assert_schema(items, {"type": "array", "items": TASK_SCHEMA})
    ids = [item["id"] for item in items]
    assert all(task["id"] in ids for task in own)
    assert other["id"] not in ids
    assert all(item["owner"] == "alice" for item in items)
    assert ids == sorted(ids)


@pytest.mark.parametrize("value", ["other", "", "TRUE", "1"], ids=["word", "empty", "case", "number"])
def test_invalid_archive_query(alice_client, value):
    result = alice_client.get_json("/tasks", params={"include_archived": value}, expect_status=400)
    assert result == {"error": "invalid_fields"}


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_archived_other_user_forbidden(alice_client, bob_client, task_factory, method):
    task = make_state(alice_client, task_factory, "archived")
    path = f"/tasks/{task['id']}"
    kwargs = {"json": {"title": "stolen"}} if method == "PUT" else {}
    response = bob_client.request(method, path, expect_status=403, **kwargs)
    assert response.json() == {"error": "forbidden"}
    assert alice_client.get_json(path) == task
