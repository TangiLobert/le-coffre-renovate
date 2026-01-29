from typing import Protocol


class SsoEncryptionGateway(Protocol):
    def encrypt(self, plaintext: str) -> str:
        """Encrypts the given plaintext for SSO configuration."""
        ...

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts the given ciphertext for SSO configuration."""
        ...
