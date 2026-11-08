@responses.activate
def test_expected_404_returns_response():
    responses.get(f"{BASE}/tasks/404", json={"error": "not_found"}, status=404)
    with APIClient(BASE, max_retries=0) as client:
        response = client.request("GET", "/tasks/404", expect_status=404)
        assert response.status_code == 404
        assert response.json() == {"error": "not_found"}


@responses.activate
def test_delete_204_has_no_json():
    responses.delete(f"{BASE}/tasks/1", status=204)
    with APIClient(BASE, max_retries=0) as client:
        response = client.delete("/tasks/1", expect_status=204)
        assert response.content == b""


@responses.activate
def test_invalid_json_is_parse_error():
    responses.get(f"{BASE}/broken", body="not-json", status=200)
    with APIClient(BASE, max_retries=0) as client:
        with pytest.raises(requests.exceptions.JSONDecodeError):
            client.get_json("/broken")


def test_patch_at_used_session():
    from unittest.mock import patch
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"items": []}'
    with APIClient(BASE, timeout=3, max_retries=0) as client:
        with patch.object(client.session, "request", return_value=response) as mocked:
            assert client.get_json("/tasks") == {"items": []}
            mocked.assert_called_once_with("GET", f"{BASE}/tasks", timeout=3)
