"""补充 HTTP 断言的只读落库检查；不通过 SQL 修改业务数据。"""
from contextlib import closing
import sqlite3

import pytest

pytestmark = pytest.mark.integration


def read_task(db_path, task_id):
    with closing(sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        return db.execute("SELECT title,status,owner FROM tasks WHERE id=? AND owner=?", (task_id, "alice")).fetchone()


def test_update_is_persisted(alice_client, task_factory, local_api_db):
    task = task_factory("before")
    assert read_task(local_api_db, task["id"]) == ("before", "open", "alice")
    alice_client.put_json(f"/tasks/{task['id']}", {"title": "changed", "status": "done"})
    assert read_task(local_api_db, task["id"]) == ("changed", "done", "alice")


def test_rejected_update_does_not_partially_write(alice_client, task_factory, local_api_db):
    task = task_factory("before")
    alice_client.put_json(f"/tasks/{task['id']}", {"title": "changed", "status": "invalid"}, expect_status=400)
    assert read_task(local_api_db, task["id"]) == ("before", "open", "alice")
