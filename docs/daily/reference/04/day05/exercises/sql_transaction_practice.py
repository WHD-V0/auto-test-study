from contextlib import closing
import sqlite3

with closing(sqlite3.connect("reports/learning/sql-01.sqlite3")) as db:
    db.execute("PRAGMA foreign_keys=ON")
    query = "SELECT id FROM tasks WHERE owner='alice' AND status='open'"
    print("before index:", db.execute("EXPLAIN QUERY PLAN " + query).fetchall())
    db.execute("BEGIN")
    try:
        db.execute("UPDATE tasks SET status=? WHERE id=?", ("done", 101))
        assert db.execute("SELECT status FROM tasks WHERE id=101").fetchone() == ("done",)
        db.execute("CREATE INDEX idx_practice_owner_status ON tasks(owner,status)")
        print("with index:", db.execute("EXPLAIN QUERY PLAN " + query).fetchall())
    finally:
        db.rollback()
    assert db.execute("SELECT status FROM tasks WHERE id=101").fetchone() == ("open",)
    print("rollback verified")
