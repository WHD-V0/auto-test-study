"""客户端外部可观察行为：重试副作用、日志内容、原始响应。"""
import logging

import pytest
import requests
import responses

from core.api_client import APIClient, APIError

BASE = "https://client.test"


@responses.activate
def test_get_retries_transient_status():
    responses.get(f"{BASE}/tasks", status=503)
    responses.get(f"{BASE}/tasks", json={"items": []}, status=200)
    with APIClient(BASE, max_retries=1) as client:
        assert client.get_json("/tasks") == {"items": []}
    assert len(responses.calls) == 2


@responses.activate
@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE"])
def test_write_is_not_replayed(method):
    responses.add(method, f"{BASE}/tasks", json={"error": "unavailable"}, status=503)
    with APIClient(BASE, max_retries=2) as client:
        assert client.request(method, "/tasks", expect_status=503).status_code == 503
    assert len(responses.calls) == 1


@responses.activate
def test_exhausted_get_can_assert_last_status():
    responses.get(f"{BASE}/tasks", status=503)
    with APIClient(BASE, max_retries=1) as client:
        client.request("GET", "/tasks", expect_status=503)
    assert len(responses.calls) == 2


@responses.activate
def test_timeout_is_not_replayed():
    responses.post(f"{BASE}/tasks", body=requests.ReadTimeout("secret-url"))
    with APIClient(BASE, max_retries=2) as client:
        with pytest.raises(APIError, match="ReadTimeout") as caught:
            client.post_json("/tasks", {"title": "test"})
    assert "secret-url" not in str(caught.value)
    assert len(responses.calls) == 1


@responses.activate
def test_logs_and_status_error_exclude_payloads(caplog):
    responses.post(f"{BASE}/login", json={"token": "secret-response"}, status=400)
    with APIClient(BASE, max_retries=0) as client:
        client.set_token("secret-header")
        with caplog.at_level(logging.INFO, logger="api"):
            with pytest.raises(APIError) as caught:
                client.post_json("/login", {"password": "secret-body"}, params={"key": "secret-query"})
    combined = caplog.text + str(caught.value)
    for value in ["secret-response", "secret-header", "secret-body", "secret-query"]:
        assert value not in combined
    assert "400" in combined


@responses.activate
def test_empty_response_and_invalid_json_are_distinct():
    responses.delete(f"{BASE}/tasks/1", status=204)
    responses.get(f"{BASE}/broken", body="not-json", status=200)
    with APIClient(BASE, max_retries=0) as client:
        assert client.delete("/tasks/1", expect_status=204).content == b""
        with pytest.raises(requests.exceptions.JSONDecodeError):
            client.get_json("/broken")
