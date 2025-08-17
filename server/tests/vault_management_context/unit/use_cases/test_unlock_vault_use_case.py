import pytest

from vault_management_context.domain.entities import Share
from vault_management_context.domain.exceptions import (
    VaultNotSetupException,
    ShareReconstructionError,
)
from vault_management_context.application.use_cases.unlock_vault_use_case import (
    UnlockVaultUseCase,
)


@pytest.fixture()
def use_case(
    vault_repository, shamir_gateway, encryption_gateway, vault_session_gateway
):
    return UnlockVaultUseCase(
        vault_repository, shamir_gateway, encryption_gateway, vault_session_gateway
    )


def test_should_unlock_vault_with_valid_shares_and_decrypt_key(
    use_case,
    vault_repository,
    shamir_gateway,
    encryption_gateway,
    vault_session_gateway,
):
    # Setup vault with encrypted key - use a proper encrypted key for the test
    vault_key = "test_vault_key_12345678"
    master_secret = "master_secret"
    encrypted_key = "encrypted_vault_key_hex"

    vault_repository.save_vault_with_shares(
        nb_shares=3, threshold=2, encrypted_key=encrypted_key
    )

    shares = [Share(0, "share0"), Share(1, "share1")]

    shamir_gateway.set_reconstructed_secret(master_secret)
    encryption_gateway.set_decrypted_key(vault_key)

    use_case.execute(shares)

    # Verify the decrypted key is now in session
    decrypted_key = vault_session_gateway.get_decrypted_key()
    assert decrypted_key == vault_key


def test_should_fail_when_vault_is_not_setup(use_case):
    shares = [Share(0, "share0"), Share(1, "share1")]

    with pytest.raises(VaultNotSetupException):
        use_case.execute(shares)


def test_should_fail_when_not_enough_shares_provided(use_case, vault_repository):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)
    shares = [Share(0, "share0")]

    with pytest.raises(ShareReconstructionError):
        use_case.execute(shares)


def test_should_fail_when_shamir_reconstruction_fails(
    use_case, vault_repository, shamir_gateway
):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)
    shares = [Share(0, "invalid_share0"), Share(1, "invalid_share1")]
    shamir_gateway.set_reconstruction_failure(True)

    with pytest.raises(ShareReconstructionError):
        use_case.execute(shares)
