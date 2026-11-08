import responses
from core.api_client import APIClient

BASE = "https://client.test"


@responses.activate
def test_diagnose_invalid_json():
    responses.get(f"{BASE}/broken", body="not-json", status=200)
    with APIClient(BASE, max_retries=0) as client:
        client.get_json("/broken")  # 故意不捕获：观察JSONDecodeError。


@responses.activate
def test_diagnose_bad_status():
    responses.get(f"{BASE}/tasks", status=503)
    with APIClient(BASE, max_retries=0) as client:
        client.get_json("/tasks")  # 默认期望200，故意观察APIError。
