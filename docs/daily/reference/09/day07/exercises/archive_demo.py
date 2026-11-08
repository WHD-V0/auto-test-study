import os
import requests

base = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765").rstrip("/")


def login(session, user):
    response = session.post(f"{base}/login", json={"username": user, "password": f"{user}-pass"}, timeout=3)
    assert response.status_code == 200
    session.headers["Authorization"] = "Bearer " + response.json()["token"]


with requests.Session() as alice, requests.Session() as bob:
    alice.trust_env = bob.trust_env = False
    login(alice, "alice")
    login(bob, "bob")
    response = alice.post(f"{base}/tasks", json={"title": "archive-demo"}, timeout=3)
    assert response.status_code == 201
    task = response.json()
    path = f"{base}/tasks/{task['id']}"
    try:
        assert alice.put(path, json={"title": "illegal", "status": "archived"}, timeout=3).status_code == 409
        assert alice.get(path, timeout=3).json() == task
        assert alice.put(path, json={"status": "done"}, timeout=3).status_code == 200
        response = alice.put(path, json={"status": "archived"}, timeout=3)
        assert response.status_code == 200
        assert response.json()["status"] == "archived"
        assert alice.get(path, timeout=3).json()["status"] == "archived"
        assert bob.get(path, timeout=3).status_code == 403
        assert alice.put(path, json={"title": "blocked"}, timeout=3).status_code == 409
        print("归档成功、非法转换无副作用、Bob越权拒绝、title锁定：全部通过")
    finally:
        assert alice.delete(path, timeout=3).status_code in (204, 404)
