from typing import List

from vault_management_context.domain.entities import Share


def test_can_create_the_vault(client, vault_repository, shamir_gateway):
    nb_shares = 3
    threshold = 2
    expected_shares: List[Share] = [Share(0, "1"), Share(1, "2"), Share(2, "3")]
    shamir_gateway.set(expected_shares)

    response = client.post(
        "/api/vault/setup",
        json={
            "nb_shares": nb_shares,
            "threshold": threshold,
        },
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["shares"] == [share.to_dict() for share in expected_shares]

    generated_vault = vault_repository.get()
    assert generated_vault.nb_shares == nb_shares
    assert generated_vault.threshold == threshold


def test_should_fail_to_create_vault_with_invalid_share_count(client):
    nb_shares = 1

    response = client.post(
        "/api/vault/setup",
        json={
            "nb_shares": nb_shares,
            "threshold": 1,
        },
    )

    assert response.status_code == 400
    response_data = response.json()
    assert "Share count must be at least 2" in response_data["detail"]


def test_should_fail_to_create_vault_with_invalid_threshold(client):
    threshold = 1

    response = client.post(
        "/api/vault/setup",
        json={
            "nb_shares": 3,
            "threshold": threshold,
        },
    )

    assert response.status_code == 400
    response_data = response.json()
    assert "Threshold must be at least 2" in response_data["detail"]


def test_should_fail_to_create_vault_with_threshold_exceeding_shares(client):
    nb_shares = 3
    threshold = 4

    response = client.post(
        "/api/vault/setup",
        json={
            "nb_shares": nb_shares,
            "threshold": threshold,
        },
    )

    assert response.status_code == 400
    response_data = response.json()
    assert "cannot exceed share count" in response_data["detail"]


def test_should_fail_to_create_vault_twice(client, vault_repository):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)

    response = client.post(
        "/api/vault/setup",
        json={
            "nb_shares": 3,
            "threshold": 2,
        },
    )

    assert response.status_code == 400
    response_data = response.json()
    assert "already been created" in response_data["detail"]
