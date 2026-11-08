"""任务业务靶场：标准库 HTTP + SQLite。契约见 docs/API_CONTRACT.md。"""
from __future__ import annotations

import argparse
import json
import sqlite3
import threading
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from uuid import uuid4

# 公开演示数据，不能作为实际环境的认证实现。
DEMO_USERS = {"alice": "alice-pass", "bob": "bob-pass"}


class TaskServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.tokens: dict[str, str] = {}
        self.token_lock = threading.Lock()
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, status TEXT NOT NULL, owner TEXT NOT NULL
            )""")
            db.commit()
        super().__init__(address, TaskHandler)


class TaskHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 不使用默认访问日志，避免记录 URL/query 等原始输入。
        pass

    def reply(self, status, body=None, headers=None):
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Request-ID", uuid4().hex)
        if body is not None:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def error(self, status, code):
        self.reply(status, {"error": code})

    def read_object(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                raise ValueError("invalid length")
            value = json.loads(self.rfile.read(size))
            if not isinstance(value, dict):
                raise ValueError("expected object")
            return value
        except (ValueError, UnicodeDecodeError):
            self.error(400, "invalid_json_object")
            return None

    def dispatch(self):
        path = urlsplit(self.path).path
        if path == "/health":
            if self.command != "GET":
                return self.error(405, "method_not_allowed")
            return self.reply(200, {"status": "ok"})
        if path == "/login":
            if self.command != "POST":
                return self.error(405, "method_not_allowed")
            body = self.read_object()
            if body is None:
                return
            username, password = body.get("username"), body.get("password")
            if (not isinstance(username, str) or not isinstance(password, str)
                    or DEMO_USERS.get(username) != password):
                return self.error(401, "invalid_credentials")
            token = uuid4().hex
            with self.server.token_lock:
                self.server.tokens[token] = username
            return self.reply(200, {"token": token, "username": username})

        parts = path.strip("/").split("/")
        if path != "/tasks" and not (len(parts) == 2 and parts[0] == "tasks"):
            return self.error(404, "not_found")
        auth = self.headers.get("Authorization", "")
        with self.server.token_lock:
            username = self.server.tokens.get(auth.removeprefix("Bearer ")) if auth.startswith("Bearer ") else None
        if username is None:
            return self.error(401, "unauthorized")
        # 显式提交写操作；closing 负责关闭连接，sqlite 的 with 本身不负责 close。
        with closing(sqlite3.connect(self.server.db_path, timeout=5)) as db:
            db.row_factory = sqlite3.Row
            if path == "/tasks":
                return self.collection(db, username)
            try:
                task_id = int(parts[1])
                if not 0 < task_id <= 2**63 - 1:
                    raise ValueError("invalid id")
            except ValueError:
                return self.error(404, "not_found")
            row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                return self.error(404, "not_found")
            if row["owner"] != username:
                return self.error(403, "forbidden")
            return self.resource(db, row)

    def collection(self, db, username):
        if self.command == "GET":
            parameters = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
            values = parameters.get("include_archived")
            if values is None:
                include_archived = False
            elif len(values) == 1 and values[0] in ("true", "false"):
                include_archived = values[0] == "true"
            else:
                return self.error(400, "invalid_fields")
            query = "SELECT * FROM tasks WHERE owner=?"
            if not include_archived:
                query += " AND status != 'archived'"
            query += " ORDER BY id"
            rows = db.execute(query, (username,)).fetchall()
            return self.reply(200, {"items": [dict(row) for row in rows]})
        if self.command != "POST":
            return self.error(405, "method_not_allowed")
        body = self.read_object()
        if body is None:
            return
        if set(body) != {"title"} or not self.valid_title(body.get("title")):
            return self.error(400, "invalid_fields")
        title = body["title"].strip()
        cursor = db.execute("INSERT INTO tasks(title,status,owner) VALUES (?, 'open', ?)", (title, username))
        task_id = cursor.lastrowid
        db.commit()
        self.reply(201, {"id": task_id, "title": title, "status": "open", "owner": username},
                   {"Location": f"/tasks/{task_id}"})

    @staticmethod
    def valid_title(title):
        return isinstance(title, str) and 1 <= len(title.strip()) <= 80

    def resource(self, db, row):
        if self.command == "GET":
            return self.reply(200, dict(row))
        if self.command == "DELETE":
            db.execute("DELETE FROM tasks WHERE id=?", (row["id"],))
            db.commit()
            return self.reply(204)
        if self.command != "PUT":
            return self.error(405, "method_not_allowed")
        body = self.read_object()
        if body is None:
            return
        if (not body or set(body) - {"title", "status"}
                or ("title" in body and not self.valid_title(body["title"]))
                or ("status" in body and body["status"] not in ("open", "done", "archived"))):
            return self.error(400, "invalid_fields")
        status = body.get("status", row["status"])
        # 先验证所有业务冲突，再执行一次UPDATE，避免部分写入。
        if row["status"] == "archived":
            if "title" in body or status != "archived":
                return self.error(409, "state_conflict")
        elif row["status"] == "open" and status == "archived":
            return self.error(409, "state_conflict")
        title = body["title"].strip() if "title" in body else row["title"]
        db.execute("UPDATE tasks SET title=?,status=? WHERE id=?", (title, status, row["id"]))
        db.commit()
        self.reply(200, {**dict(row), "title": title, "status": status})

    do_GET = dispatch
    do_POST = dispatch
    do_PUT = dispatch
    do_DELETE = dispatch


def create_server(db_path: Path, port: int = 0) -> TaskServer:
    return TaskServer(("127.0.0.1", port), db_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=Path("reports/tasks.sqlite3"))
    args = parser.parse_args()
    server = create_server(args.db, args.port)
    print(f"Local task API: http://127.0.0.1:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
