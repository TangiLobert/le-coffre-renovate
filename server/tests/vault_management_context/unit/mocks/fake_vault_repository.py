from vault_management_context.domain.entities import Vault
from vault_management_context.adapters.secondary.gateways.in_memory_vault_repository import (
    InMemoryVaultRepository,
)


class FakeVaultRepository(InMemoryVaultRepository):
    def save_vault_with_shares(
        self, nb_shares: int, threshold: int, encrypted_key: str = "test_key"
    ) -> None:
        self._vault = Vault(
            nb_shares=nb_shares, threshold=threshold, encrypted_key=encrypted_key
        )
