import pytest


def test_can_create_the_vault(e2e_client, vault_repository, vault_session_gateway):
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

    # Verify that encrypted key is stored in the vault
    assert generated_vault.encrypted_key is not None
    assert len(generated_vault.encrypted_key) > 0

    # Verify that decrypted key is kept in memory
    decrypted_key = vault_session_gateway.get_decrypted_key()
    assert decrypted_key is not None
    assert len(decrypted_key) > 0
