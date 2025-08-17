from typing import List

from vault_management_context.domain.entities import Share
from vault_management_context.domain.exceptions import (
    VaultNotSetupException,
    InsufficientSharesError,
    ShareReconstructionError,
)
from vault_management_context.application.gateways import VaultRepository, ShamirGateway


class UnlockVaultUseCase:
    def __init__(
        self, vault_repository: VaultRepository, shamir_gateway: ShamirGateway
    ):
        self._vault_repository = vault_repository
        self._shamir_gateway = shamir_gateway

    def execute(self, shares: List[Share]) -> None:
        vault = self._vault_repository.get()
        if vault is None:
            raise VaultNotSetupException()

        self._validate_share_count(shares, vault.threshold)

        try:
            self._shamir_gateway.reconstruct_secret(shares)
        except Exception as e:
            raise ShareReconstructionError() from e

    def _validate_share_count(
        self, shares: List[Share], required_threshold: int
    ) -> None:
        if len(shares) < required_threshold:
            raise InsufficientSharesError(len(shares), required_threshold)
