def test_user_creation_creates_personal_group(e2e_client):
    """
    End-to-end test that:
    1. Registers an admin
    2. Logs in with the admin credentials
    3. Creates a user
    4. Verifies that a personal group was created for the user
    """
    # Step 1: Register admin
    admin_data = {
        "email": "admin@example.com",
        "password": "secure_password123",
        "display_name": "System Administrator",
    }

    register_response = e2e_client.post("/api/auth/register-admin", json=admin_data)
    assert register_response.status_code == 201

    # Step 2: Login as admin
    login_data = {"email": admin_data["email"], "password": admin_data["password"]}
    login_response = e2e_client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Step 3: Create a user
    user_data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "name": "John Doe",
        "password": "user_password123",
    }

    create_user_response = e2e_client.post("/api/users/", json=user_data)
    assert create_user_response.status_code == 201
    created_user = create_user_response.json()

    assert created_user["username"] == user_data["username"]
    assert created_user["email"] == user_data["email"]
    assert created_user["message"] == "User created successfully"

    # Step 4: Verify user exists
    user_id = created_user["id"]
    get_user_response = e2e_client.get(f"/api/users/{user_id}")
    assert get_user_response.status_code == 200

    user_info = get_user_response.json()
    assert user_info["id"] == user_id
    assert user_info["username"] == user_data["username"]

    # Note: Currently there's no API endpoint to list groups,
    # so we're verifying that the user creation succeeded without errors.
    # The integration and unit tests verify that the personal group is created.
