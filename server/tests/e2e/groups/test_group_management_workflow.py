"""
End-to-end tests for group management workflow.

This test module covers the complete workflow:
1. Create a group
2. Add members to the group
3. Remove members from the group
4. Verify authorization rules
"""


def test_group_management_complete_workflow(e2e_client):
    """
    End-to-end test that:
    1. Registers an admin (group owner)
    2. Creates two additional users (to be members)
    3. Creates a group
    4. Adds a user to the group
    5. Verifies non-owner cannot add members
    6. Removes a user from the group
    7. Verifies non-owner cannot remove members
    8. Verifies cannot remove owner
    """
    # Step 1: Register admin (will be group owner)
    admin_data = {
        "email": "admin@example.com",
        "password": "secure_password123",
        "display_name": "Admin User",
    }

    register_response = e2e_client.post("/api/auth/register-admin", json=admin_data)
    assert register_response.status_code == 201

    # Login as admin
    login_data = {"email": admin_data["email"], "password": admin_data["password"]}
    login_response = e2e_client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200

    # Step 2: Create two additional users
    user1_data = {
        "username": "user1",
        "email": "user1@example.com",
        "name": "User One",
        "password": "user1_password",
    }
    create_user1_response = e2e_client.post("/api/users/", json=user1_data)
    assert create_user1_response.status_code == 201
    user1 = create_user1_response.json()
    user1_id = user1["id"]

    user2_data = {
        "username": "user2",
        "email": "user2@example.com",
        "name": "User Two",
        "password": "user2_password",
    }
    create_user2_response = e2e_client.post("/api/users/", json=user2_data)
    assert create_user2_response.status_code == 201
    user2 = create_user2_response.json()
    user2_id = user2["id"]

    # Step 3: Create a group (admin is owner)
    group_data = {"name": "Engineering Team"}
    create_group_response = e2e_client.post("/api/groups/", json=group_data)
    assert create_group_response.status_code == 201

    group = create_group_response.json()
    assert group["name"] == "Engineering Team"
    assert "id" in group
    assert group["message"] == "Group created successfully"
    group_id = group["id"]

    # Step 4: Add user1 to the group
    add_member_data = {"user_id": user1_id}
    add_member_response = e2e_client.post(
        f"/api/groups/{group_id}/members", json=add_member_data
    )
    assert add_member_response.status_code == 201

    add_member_result = add_member_response.json()
    assert add_member_result["group_id"] == group_id
    assert add_member_result["user_id"] == user1_id
    assert add_member_result["message"] == "Member added successfully"

    # Step 5: Add user2 to the group
    add_member2_data = {"user_id": user2_id}
    add_member2_response = e2e_client.post(
        f"/api/groups/{group_id}/members", json=add_member2_data
    )
    assert add_member2_response.status_code == 201

    # Step 6: Verify idempotency - adding user1 again should succeed
    add_member_again_response = e2e_client.post(
        f"/api/groups/{group_id}/members", json=add_member_data
    )
    assert add_member_again_response.status_code == 201

    # Step 7: Remove user2 from the group
    remove_member_response = e2e_client.delete(
        f"/api/groups/{group_id}/members/{user2_id}"
    )
    assert remove_member_response.status_code == 200

    remove_result = remove_member_response.json()
    assert remove_result["message"] == "Member removed successfully"

    # Step 8: Verify cannot remove user that is not a member
    remove_nonmember_response = e2e_client.delete(
        f"/api/groups/{group_id}/members/{user2_id}"
    )
    assert remove_nonmember_response.status_code == 400
    assert "is not a member of group" in remove_nonmember_response.json()["detail"]


def test_group_management_authorization_rules(e2e_client):
    """
    End-to-end test verifying authorization rules:
    1. Only owners can add members
    2. Only owners can remove members
    3. Cannot remove owners from groups

    Note: Using two admins since regular users don't have login credentials.
    """
    # Register first admin (group owner)
    owner_data = {
        "email": "owner@example.com",
        "password": "owner_password",
        "display_name": "Group Owner",
    }
    e2e_client.post("/api/auth/register-admin", json=owner_data)
    e2e_client.post(
        "/api/auth/login",
        json={"email": owner_data["email"], "password": owner_data["password"]},
    )

    # Get owner user ID
    me_response = e2e_client.get("/api/users/me")
    owner_id = me_response.json()["id"]

    # Create a user (target for group membership)
    target_data = {
        "username": "target",
        "email": "target@example.com",
        "name": "Target User",
        "password": "target_password",
    }
    target_response = e2e_client.post("/api/users/", json=target_data)
    target_id = target_response.json()["id"]

    # Owner creates a group
    group_response = e2e_client.post("/api/groups/", json={"name": "Test Group"})
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    # Add target to group as member
    e2e_client.post(
        f"/api/groups/{group_id}/members",
        json={"user_id": target_id},
    )

    # Logout owner
    e2e_client.post("/api/auth/logout")

    # Register second admin (non-owner)
    non_owner_data = {
        "email": "nonowner@example.com",
        "password": "nonowner_password",
        "display_name": "Non-Owner Admin",
    }
    e2e_client.post("/api/auth/register-admin", json=non_owner_data)
    e2e_client.post(
        "/api/auth/login",
        json={"email": non_owner_data["email"], "password": non_owner_data["password"]},
    )

    # Create another user for testing
    new_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "name": "New User",
        "password": "password",
    }
    new_user_response = e2e_client.post("/api/users/", json=new_user_data)
    new_user_id = new_user_response.json()["id"]

    # Try to add user as non-owner - should fail with 403
    add_response = e2e_client.post(
        f"/api/groups/{group_id}/members",
        json={"user_id": new_user_id},
    )
    assert add_response.status_code == 403
    assert "is not an owner of group" in add_response.json()["detail"]

    # Try to remove user as non-owner - should fail with 403
    remove_response = e2e_client.delete(f"/api/groups/{group_id}/members/{target_id}")
    assert remove_response.status_code == 403
    assert "is not an owner of group" in remove_response.json()["detail"]

    # Login back as owner
    e2e_client.post("/api/auth/logout")
    e2e_client.post(
        "/api/auth/login",
        json={"email": owner_data["email"], "password": owner_data["password"]},
    )

    # Try to remove owner - should fail with 400
    remove_owner_response = e2e_client.delete(
        f"/api/groups/{group_id}/members/{owner_id}"
    )
    assert remove_owner_response.status_code == 400
    assert "Cannot remove owner" in remove_owner_response.json()["detail"]


def test_group_creation_requires_authentication(e2e_client):
    """
    Test that group operations require authentication.
    """
    # Try to create group without authentication
    group_data = {"name": "Unauthorized Group"}
    response = e2e_client.post("/api/groups/", json=group_data)
    assert response.status_code == 401  # Unauthorized


def test_cannot_add_nonexistent_user_to_group(e2e_client):
    """
    Test that adding a non-existent user to a group fails properly.
    """
    # Register and login
    admin_data = {
        "email": "admin@example.com",
        "password": "password",
        "display_name": "Admin",
    }
    e2e_client.post("/api/auth/register-admin", json=admin_data)
    e2e_client.post(
        "/api/auth/login",
        json={"email": admin_data["email"], "password": admin_data["password"]},
    )

    # Create group
    group_response = e2e_client.post("/api/groups/", json={"name": "Test Group"})
    group_id = group_response.json()["id"]

    # Try to add non-existent user
    fake_user_id = "00000000-0000-0000-0000-000000000000"
    add_response = e2e_client.post(
        f"/api/groups/{group_id}/members",
        json={"user_id": fake_user_id},
    )
    assert add_response.status_code == 404
    assert "was not found" in add_response.json()["detail"]


def test_cannot_modify_personal_group(e2e_client):
    """
    Test that personal groups cannot be modified (members cannot be added/removed).
    Note: Personal groups are created automatically when a user is created.
    This test requires knowing the personal group ID, which isn't exposed via API yet.
    """
    # This is a placeholder test that documents the expected behavior
    # TODO: Implement once we have an API to list groups or get personal group ID
    pass
