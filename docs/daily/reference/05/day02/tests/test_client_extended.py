import json
from urllib.parse import urlparse, parse_qs
import pytest
import requests
import responses
from core.api_client import APIClient, APIError

BASE = "https://client.test"


@responses.activate
def test_query_is_sent():
    responses.get(f"{BASE}/search", json={"items": []}, status=200)
    with APIClient(BASE, timeout=3, max_retries=0) as client:
        assert client.get_json("/search", params={"q": "hello world", "page": 2}) == {"items": []}
    assert len(responses.calls) == 1
    sent = responses.calls[0].request
    assert sent.method == "GET"
    assert parse_qs(urlparse(sent.url).query) == {"q": ["hello world"], "page": ["2"]}


@responses.activate
def test_json_body_is_sent():
    responses.post(f"{BASE}/tasks", json={"id": 7}, status=201)
    body = {"title": "client-test"}
    with APIClient(BASE, max_retries=0) as client:
        assert client.post_json("/tasks", body) == {"id": 7}
    assert len(responses.calls) == 1
    sent = responses.calls[0].request
    assert sent.method == "POST"
    assert sent.headers["Content-Type"] == "application/json"
    assert json.loads(sent.body) == body
