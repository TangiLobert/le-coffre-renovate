from uuid import UUID


def test_can_update_password(e2e_client, setup):
    user_id = str(UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e6"))
    folder = "Update Test Folder"

    # Create a password to update
    create_response = e2e_client.post(
        "/api/passwords",
        json={
            "user_id": user_id,
            "name": "Password To Update",
            "password": "StrongP@ssw0rd!",
            "folder": folder,
        },
    )
    assert create_response.status_code == 201
    password_id = create_response.json()["id"]

    # Update the created password
    update_response = e2e_client.put(
        f"/api/passwords/{password_id}",
        json={
            "user_id": user_id,
            "name": "Updated Password Name",
            "password": "NewStrongP@ssw0rd!",
            "folder": folder,
        },
    )
    assert update_response.status_code == 201


def test_update_nonexistent_password(e2e_client, setup):
    user_id = str(UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e6"))
    nonexistent_password_id = str(UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e7"))

    # Attempt to update a non-existent password
    update_response = e2e_client.put(
        f"/api/passwords/{nonexistent_password_id}",
        json={
            "user_id": user_id,
            "name": "Updated Password Name",
            "password": "NewStrongP@ssw0rd!",
            "folder": "folder",
        },
    )
    assert update_response.status_code == 404


def test_update_password_invalid_user(e2e_client, setup):
    valid_user_id = str(UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e6"))
    invalid_user_id = str(UUID("8d742e0e-bb76-4728-83ef-8d546d7c62e8"))
    folder = "Invalid User Test Folder"

    # Create a password with a valid user
    create_response = e2e_client.post(
        "/api/passwords",
        json={
            "user_id": valid_user_id,
            "name": "Password For Invalid User Test",
            "password": "StrongP@ssw0rd!",
            "folder": folder,
        },
    )
    assert create_response.status_code == 201
    password_id = create_response.json()["id"]

    # Attempt to update the password with an invalid user
    update_response = e2e_client.put(
        f"/api/passwords/{password_id}",
        json={
            "user_id": invalid_user_id,
            "name": "Updated Password Name",
            "password": "NewStrongP@ssw0rd!",
            "folder": folder,
        },
    )
    assert update_response.status_code == 404
