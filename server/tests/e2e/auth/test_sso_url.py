def test_get_sso_url_accessible_without_auth(e2e_client, setup):
    """
    Test that the SSO URL endpoint is accessible without authentication.
    This is crucial as users need to get the SSO URL before being authenticated.
    """
    # Act: Call the endpoint without any authentication headers
    response = e2e_client.get("/api/auth/sso/url")

    # Assert: Should be accessible without authentication
    assert response.status_code == 200
    assert response.json()  # Should return a URL
