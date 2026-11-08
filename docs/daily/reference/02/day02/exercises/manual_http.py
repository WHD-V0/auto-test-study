import os
import requests

BASE = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765").rstrip("/")


def login(username="alice"):
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.post(f"{BASE}/login", json={
            "username": username, "password": f"{username}-pass"}, timeout=3)
        assert response.status_code == 200
        session.headers["Authorization"] = "Bearer " + response.json()["token"]
        return session
    except Exception:
        session.close()
        raise


def checked(session, method, path, expected, **kwargs):
    response = session.request(method, f"{BASE}{path}", timeout=3, **kwargs)
    assert response.status_code == expected, (method, path, expected, response.status_code)
    return response
