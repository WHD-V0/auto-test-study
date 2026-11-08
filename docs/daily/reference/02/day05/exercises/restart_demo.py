from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import requests
from sandbox.task_api import create_server


def start(db_path):
    server = create_server(db_path)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def token(session, base):
    response = session.post(f"{base}/login", json={"username": "alice", "password": "alice-pass"}, timeout=3)
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["token"]}


with TemporaryDirectory() as directory, requests.Session() as session:
    session.trust_env = False
    db = Path(directory) / "persist.sqlite3"
    server, thread, base = start(db)
    try:
        old_headers = token(session, base)
        response = session.post(f"{base}/tasks", headers=old_headers, json={"title": "restart-check"}, timeout=3)
        assert response.status_code == 201
        task = response.json()
    finally:
        stop(server, thread)
    # 端口可以不同；关键是同一个数据库文件，且服务实例已换新。
    server, thread, base = start(db)
    try:
        path = f"{base}/tasks/{task['id']}"
        assert session.get(path, headers=old_headers, timeout=3).status_code == 401
        new_headers = token(session, base)
        response = session.get(path, headers=new_headers, timeout=3)
        assert response.status_code == 200
        assert response.json() == task
        assert session.delete(path, headers=new_headers, timeout=3).status_code == 204
        print("旧token=401；新登录后同ID任务仍在；已清理")
    finally:
        stop(server, thread)
