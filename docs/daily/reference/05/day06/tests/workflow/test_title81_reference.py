def test_title81_is_rejected(alice_client):
    before = alice_client.get_json("/tasks")
    assert alice_client.post_json("/tasks", {"title": "x" * 81}, expect_status=400) == {"error": "invalid_fields"}
    assert alice_client.get_json("/tasks") == before
