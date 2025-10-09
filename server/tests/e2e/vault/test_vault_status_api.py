def test_can_access_vault_status(e2e_client, admin_token):
    # Initial status should be NOT_SETUP
    not_setup_response = e2e_client.get("/api/vault/status")

    assert not_setup_response.status_code == 200
    not_setup_data = not_setup_response.json()

    assert not_setup_data["status"] == "NOT_SETUP"

    # Setup vault - will be in PENDING status
    setup_response = e2e_client.post(
        "/api/vault/setup",
        json={
            "nb_shares": 5,
            "threshold": 3,
        },
    )
    assert setup_response.status_code == 201
    setup_id = setup_response.json()["setup_id"]
    
    # Check PENDING status
    pending_response = e2e_client.get("/api/vault/status")
    assert pending_response.status_code == 200
    assert pending_response.json()["status"] == "PENDING"
    
    # Validate to complete setup - will be LOCKED
    validate_response = e2e_client.post(
        "/api/vault/validate-setup",
        json={"setup_id": setup_id},
    )
    assert validate_response.status_code == 200
    
    # After validation, should be LOCKED
    locked_response = e2e_client.get("/api/vault/status")
    assert locked_response.status_code == 200
    locked_data = locked_response.json()
    assert locked_data["status"] == "LOCKED"
