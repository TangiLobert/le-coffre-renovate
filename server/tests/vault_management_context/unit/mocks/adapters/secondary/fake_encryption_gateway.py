from vault_management_context.application.gateways.encryption_gateway import (
    EncryptionGateway,
)


class FakeEncryptionGateway(EncryptionGateway):
    def __init__(self):
        self._encrypted_key = None
        self._decrypted_key = None

    def set_encrypted_key(self, encrypted_key: str) -> None:
        self._encrypted_key = encrypted_key

    def set_decrypted_key(self, decrypted_key: str) -> None:
        self._decrypted_key = decrypted_key

    def generate_encrypted_key(self, master_key: str) -> str:
        if self._encrypted_key is None:
            raise ValueError("No encrypted key configured for fake")
        return self._encrypted_key

    def decrypt_key(self, encrypted_key: str, master_key: str) -> str:
        if self._decrypted_key is None:
            raise ValueError("No decrypted key configured for fake")
        return self._decrypted_key
