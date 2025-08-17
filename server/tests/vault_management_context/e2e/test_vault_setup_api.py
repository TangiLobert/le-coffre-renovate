import pytest


def test_can_create_the_vault(e2e_client, vault_repository):
    response = e2e_client.post(
        "/api/vault/setup",
        json={
            "nb_shares": 5,
            "threshold": 3,
        },
    )

    assert response.status_code == 201
    response_data = response.json()

    shares = response_data["shares"]
    assert len(shares) == 5

    for share in shares:
        assert "index" in share and isinstance(share["index"], int)
        assert (
            "secret" in share
            and isinstance(share["secret"], str)
            and len(share["secret"]) > 20
        )
        int(share["secret"], 16)

    generated_vault = vault_repository.get()
    assert generated_vault.nb_shares == 5
    assert generated_vault.threshold == 3
