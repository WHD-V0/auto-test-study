@responses.activate
def test_logs_exclude_secrets(caplog):
    import logging
    responses.post(f"{BASE}/login", json={"token": "secret-response-test"}, status=400)
    with APIClient(BASE, max_retries=0) as client:
        client.set_token("secret-header-test")
        with caplog.at_level(logging.INFO, logger="api"):
            with pytest.raises(APIError) as caught:
                client.post_json("/login", {"password": "secret-body-test"},
                                 params={"key": "secret-query-test"})
    text = caplog.text + str(caught.value)
    assert "POST" in text
    assert "400" in text
    for secret in ["secret-response-test", "secret-header-test", "secret-body-test", "secret-query-test"]:
        assert secret not in text
