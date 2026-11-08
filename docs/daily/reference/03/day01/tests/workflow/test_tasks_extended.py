import pytest
from core.validator import assert_schema
from tests.workflow.test_tasks import TASK_SCHEMA


def test_my_crud(alice_client, task_factory):
    task = task_factory("my-crud")
    path = f"/tasks/{task['id']}"
    assert_schema(task, TASK_SCHEMA)
    assert task["owner"] == "alice"
    assert task["status"] == "open"
    assert alice_client.get_json(path) == task
    expected = {**task, "title": "changed", "status": "done"}
    assert alice_client.put_json(path, {"title": "changed", "status": "done"}) == expected
    assert alice_client.get_json(path) == expected
    deleted = alice_client.delete(path, expect_status=204)
    assert deleted.content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}
