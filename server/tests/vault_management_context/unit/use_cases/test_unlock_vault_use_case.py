import pytest

from vault_management_context.domain.entities import Share
from vault_management_context.domain.exceptions import (
    VaultNotSetupException,
    InsufficientSharesError,
    ShareReconstructionError,
)
from vault_management_context.application.use_cases.unlock_vault_use_case import (
    UnlockVaultUseCase,
)


def test_should_unlock_vault_with_valid_shares(vault_repository, shamir_gateway):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)
    shares = [Share(0, "share0"), Share(1, "share1")]
    shamir_gateway.set_reconstructed_secret("master_secret")
    use_case = UnlockVaultUseCase(vault_repository, shamir_gateway)

    use_case.execute(shares)


def test_should_fail_when_vault_is_not_setup(vault_repository, shamir_gateway):
    shares = [Share(0, "share0"), Share(1, "share1")]
    use_case = UnlockVaultUseCase(vault_repository, shamir_gateway)

    with pytest.raises(VaultNotSetupException):
        use_case.execute(shares)


def test_should_fail_when_not_enough_shares_provided(vault_repository, shamir_gateway):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)
    shares = [Share(0, "share0")]
    use_case = UnlockVaultUseCase(vault_repository, shamir_gateway)

    with pytest.raises(InsufficientSharesError):
        use_case.execute(shares)


def test_should_fail_when_shamir_reconstruction_fails(vault_repository, shamir_gateway):
    vault_repository.save_vault_with_shares(nb_shares=3, threshold=2)
    shares = [Share(0, "invalid_share0"), Share(1, "invalid_share1")]
    shamir_gateway.set_reconstruction_failure(True)
    use_case = UnlockVaultUseCase(vault_repository, shamir_gateway)

    with pytest.raises(ShareReconstructionError):
        use_case.execute(shares)
