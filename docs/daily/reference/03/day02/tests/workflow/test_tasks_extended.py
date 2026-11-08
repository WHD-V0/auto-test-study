@pytest.mark.parametrize("token", [None, "invalid-token"], ids=["missing", "invalid"])
def test_auth_missing_or_invalid(anonymous_client, alice_client, token):
    before = alice_client.get_json("/tasks")
    if token is not None:
        anonymous_client.set_token(token)
    result = anonymous_client.post_json("/tasks", {"title": "should-not-exist"}, expect_status=401)
    assert result == {"error": "unauthorized"}
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"], ids=["GET", "PUT", "DELETE"])
def test_other_user_access(alice_client, bob_client, task_factory, method):
    task = task_factory("alice-private")
    path = f"/tasks/{task['id']}"
    kwargs = {"json": {"title": "stolen"}} if method == "PUT" else {}
    response = bob_client.request(method, path, expect_status=403, **kwargs)
    assert response.json() == {"error": "forbidden"}
    assert alice_client.get_json(path) == task
