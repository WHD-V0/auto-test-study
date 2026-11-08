def test_invalid_title_number(alice_client):
    before = alice_client.get_json("/tasks")
    result = alice_client.post_json("/tasks", {"title": 123}, expect_status=400)
    assert result == {"error": "invalid_fields"}
    after = alice_client.get_json("/tasks")
    assert after == before
