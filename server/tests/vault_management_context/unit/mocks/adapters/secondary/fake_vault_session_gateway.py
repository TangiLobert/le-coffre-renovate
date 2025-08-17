from vault_management_context.application.gateways.vault_session_gateway import (
    VaultSessionGateway,
)


class FakeVaultSessionGateway(VaultSessionGateway):
    def __init__(self):
        self._decrypted_key = None

    def store_decrypted_key(self, decrypted_key: str) -> None:
        self._decrypted_key = decrypted_key

    def get_decrypted_key(self) -> str:
        if self._decrypted_key is None:
            raise ValueError("No decrypted key in session")
        return self._decrypted_key

    def clear_decrypted_key(self) -> None:
        self._decrypted_key = None
