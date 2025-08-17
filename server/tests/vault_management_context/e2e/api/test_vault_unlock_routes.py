def test_can_unlock_vault_with_valid_shares(client, vault_repository, shamir_gateway):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)
    shamir_gateway.set_reconstructed_secret("master_secret")

    response = client.post(
        "/api/vault/unlock",
        json={
            "shares": [
                {"index": 0, "secret": "share0"},
                {"index": 1, "secret": "share1"},
            ]
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Vault unlocked successfully"


def test_should_fail_to_unlock_when_vault_not_setup(client):
    response = client.post(
        "/api/vault/unlock",
        json={
            "shares": [
                {"index": 0, "secret": "share0"},
                {"index": 1, "secret": "share1"},
            ]
        },
    )

    assert response.status_code == 400
    response_data = response.json()
    assert "Vault has not been setup yet" in response_data["detail"]


def test_should_fail_to_unlock_with_insufficient_shares(client, vault_repository):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)

    response = client.post(
        "/api/vault/unlock",
        json={"shares": [{"index": 0, "secret": "share0"}]},
    )

    assert response.status_code == 400
    response_data = response.json()
    assert "Not enough shares provided" in response_data["detail"]


def test_should_fail_to_unlock_with_invalid_shares(
    client, vault_repository, shamir_gateway
):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)
    shamir_gateway.set_reconstruction_failure(True)

    response = client.post(
        "/api/vault/unlock",
        json={
            "shares": [
                {"index": 0, "secret": "invalid_share0"},
                {"index": 1, "secret": "invalid_share1"},
            ]
        },
    )

    assert response.status_code == 400
    response_data = response.json()
    assert "Failed to reconstruct secret" in response_data["detail"]


def test_should_fail_to_unlock_with_empty_shares_list(client, vault_repository):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)

    response = client.post(
        "/api/vault/unlock",
        json={"shares": []},
    )

    assert response.status_code == 422
    response_data = response.json()
    assert "at least 1 item" in str(response_data)
