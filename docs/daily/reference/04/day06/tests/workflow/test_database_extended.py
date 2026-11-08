from contextlib import closing
import sqlite3


def read_task(db_path, task_id):
    uri = db_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as db:
        return db.execute("SELECT title,status,owner FROM tasks WHERE id=? AND owner=?",
                          (task_id, "alice")).fetchone()


def test_delete_is_persisted(alice_client, task_factory, local_api_db):
    task = task_factory("delete-check")
    path = f"/tasks/{task['id']}"
    assert read_task(local_api_db, task["id"]) == ("delete-check", "open", "alice")
    assert alice_client.delete(path, expect_status=204).content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}
    assert read_task(local_api_db, task["id"]) is None


def test_invalid_update_keeps_database_unchanged(alice_client, task_factory, local_api_db):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "after", "status": "bad"}, expect_status=400)
    assert alice_client.get_json(path) == task
    assert read_task(local_api_db, task["id"]) == ("before", "open", "alice")
