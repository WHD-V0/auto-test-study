import os
import requests
from core.api_client import APIClient

base = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765")
with requests.Session() as session:
    session.trust_env = False
    response = session.get(f"{base}/health", timeout=3)
    assert response.status_code == 200
    direct = response.json()
with APIClient(base, timeout=3, max_retries=0) as client:
    client.session.trust_env = False
    wrapped = client.get_json("/health")
assert direct == wrapped == {"status": "ok"}
print("requests与APIClient业务结果一致")
