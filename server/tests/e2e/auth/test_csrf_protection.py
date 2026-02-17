"""
E2E test for CSRF protection.
Tests the full CSRF lifecycle: token generation, validation, rejection, exemptions.
"""


def test_csrf_protection_full_flow(e2e_client):
    """
    Complete CSRF protection flow:
    1. Unauthenticated user cannot get a CSRF token
    2. Registration and login are exempt from CSRF
    3. Authenticated user can get a CSRF token
    4. GET requests work without CSRF token
    5. POST/PUT/DELETE without CSRF token are rejected
    6. POST with invalid CSRF token is rejected
    7. POST with valid CSRF token succeeds
    8. Same token can be reused across multiple requests
    9. Regenerating a token invalidates the previous one
    10. Refresh token endpoint is exempt from CSRF
    """

    # 1. Unauthenticated user cannot get a CSRF token
    response = e2e_client.get("/api/auth/csrf-token")
    assert response.status_code == 401

    # 2. Registration and login are exempt from CSRF
    e2e_client.post(
        "/api/auth/register-admin",
        json={
            "email": "csrf@example.com",
            "password": "password123",
            "display_name": "CSRF Test Admin",
        },
    )

    login_response = e2e_client.post(
        "/api/auth/login",
        json={"email": "csrf@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200

    # 3. Authenticated user can get a CSRF token
    token_response = e2e_client.get("/api/auth/csrf-token")
    assert token_response.status_code == 200
    csrf_token = token_response.json()["csrf_token"]
    assert len(csrf_token) > 0

    # 4. GET requests work without CSRF token
    response = e2e_client.get("/api/groups")
    assert response.status_code == 200

    # 5a. POST without CSRF token is rejected
    e2e_client.disable_auto_csrf()

    response = e2e_client.post(
        "/api/groups/",
        json={"name": "No CSRF", "description": "Should fail"},
    )
    assert response.status_code == 403
    assert "CSRF token missing" in response.json()["detail"]

    # 5b. PUT without CSRF token is rejected
    me = e2e_client.get("/api/users/me").json()
    response = e2e_client.put(
        f"/api/groups/{me['personal_group_id']}",
        json={"name": "No CSRF", "description": "Should fail"},
    )
    assert response.status_code == 403
    assert "CSRF token missing" in response.json()["detail"]

    # 6. POST with invalid CSRF token is rejected
    response = e2e_client.post(
        "/api/groups/",
        json={"name": "Bad CSRF", "description": "Should fail"},
        headers={"X-CSRF-Token": "invalid_token_12345"},
    )
    assert response.status_code == 403
    assert "Invalid or expired CSRF token" in response.json()["detail"]

    e2e_client.enable_auto_csrf()

    # 7. POST with valid CSRF token succeeds
    create_response = e2e_client.post(
        "/api/groups/",
        json={"name": "Valid CSRF Group", "description": "Should succeed"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert create_response.status_code == 201
    group_id = create_response.json()["id"]

    # 5c. DELETE without CSRF token is rejected
    e2e_client.disable_auto_csrf()
    response = e2e_client.delete(f"/api/groups/{group_id}")
    assert response.status_code == 403
    assert "CSRF token missing" in response.json()["detail"]
    e2e_client.enable_auto_csrf()

    # 8. Same token can be reused across multiple requests
    for i in range(3):
        response = e2e_client.post(
            "/api/groups/",
            json={"name": f"Reuse Token {i}", "description": "Multi-use"},
            headers={"X-CSRF-Token": csrf_token},
        )
        assert response.status_code == 201

    # 9. Regenerating a token invalidates the previous one
    new_token_response = e2e_client.get("/api/auth/csrf-token")
    new_csrf_token = new_token_response.json()["csrf_token"]
    assert new_csrf_token != csrf_token

    # Old token should be rejected
    response = e2e_client.post(
        "/api/groups/",
        json={"name": "Old Token", "description": "Should fail"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 403

    # New token should work
    response = e2e_client.post(
        "/api/groups/",
        json={"name": "New Token", "description": "Should succeed"},
        headers={"X-CSRF-Token": new_csrf_token},
    )
    assert response.status_code == 201

    # 10. Refresh token endpoint is exempt from CSRF
    response = e2e_client.post("/api/auth/refresh-token")
    assert response.status_code != 403 or "CSRF" not in response.json().get(
        "detail", ""
    )
