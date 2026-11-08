def read_archive_row(db_path, task_id):
    from contextlib import closing
    import sqlite3
    with closing(sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        return db.execute("SELECT title,status,owner FROM tasks WHERE id=? AND owner=?",
                          (task_id, "alice")).fetchone()


def test_archive_is_persisted(alice_client, task_factory, local_api_db):
    task = make_state(alice_client, task_factory, "archived")
    assert read_archive_row(local_api_db, task["id"]) == (task["title"], "archived", "alice")


def test_archive_conflict_is_atomic_in_database(alice_client, task_factory, local_api_db):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "after", "status": "archived"}, expect_status=409)
    assert alice_client.get_json(path) == task
    assert read_archive_row(local_api_db, task["id"]) == ("before", "open", "alice")
