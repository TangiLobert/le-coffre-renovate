from vault_management_context.application.gateways import VaultSessionGateway


class InMemoryVaultSessionGateway(VaultSessionGateway):
    def __init__(self):
        self._decrypted_key: str | None = None

    def store_decrypted_key(self, decrypted_key: str) -> None:
        self._decrypted_key = decrypted_key

    def get_decrypted_key(self) -> str:
        if self._decrypted_key is None:
            raise ValueError("No decrypted key stored in memory")
        return self._decrypted_key

    def clear_decrypted_key(self) -> None:
        self._decrypted_key = None
