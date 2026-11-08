from core.validator import assert_schema
from tests.workflow.test_tasks import TASK_SCHEMA


def test_created_task_can_be_read(alice_client, task_factory):
    task = task_factory("my-first-http-test")
    assert_schema(task, TASK_SCHEMA)
    assert task["owner"] == "alice"
    assert task["status"] == "open"
    actual = alice_client.get_json(f"/tasks/{task['id']}")
    assert_schema(actual, TASK_SCHEMA)
    assert actual == task
