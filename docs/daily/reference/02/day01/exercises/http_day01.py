import os
import requests

base = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765")
with requests.Session() as session:
    session.trust_env = False  # 本机实验不经过系统代理。
    response = session.get(f"{base}/health", timeout=3)
    print("status:", response.status_code)
    print("content-type:", response.headers.get("Content-Type"))
    print("body:", response.json())
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
