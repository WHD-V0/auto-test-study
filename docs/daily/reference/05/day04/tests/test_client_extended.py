@responses.activate
def test_get_retry_extended():
    responses.get(f"{BASE}/tasks", status=503)
    responses.get(f"{BASE}/tasks", json={"items": []}, status=200)
    with APIClient(BASE, max_retries=1) as client:
        assert client.get_json("/tasks") == {"items": []}
    assert len(responses.calls) == 2


@responses.activate
def test_get_no_retry_extended():
    responses.get(f"{BASE}/tasks", status=503)
    with APIClient(BASE, max_retries=0) as client:
        assert client.request("GET", "/tasks", expect_status=503).status_code == 503
    assert len(responses.calls) == 1


@responses.activate
def test_post_is_not_replayed():
    responses.post(f"{BASE}/tasks", status=503)
    with APIClient(BASE, max_retries=2) as client:
        response = client.request("POST", "/tasks", json={"title": "x"}, expect_status=503)
        assert response.status_code == 503
    assert len(responses.calls) == 1
