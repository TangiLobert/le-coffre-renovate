from typing import Protocol


class EncryptionGateway(Protocol):
    def generate_encrypted_key(self, master_key: str) -> str:
        """Generate a random vault key and encrypt it using the master key

        Args:
            master_key: The key used to encrypt

        Returns:
            The encrypted vault key
        """
        ...

    def decrypt_key(self, encrypted_key: str, master_key: str) -> str:
        """Decrypt a key using the master key

        Args:
            encrypted_key: The encrypted key
            master_key: The master key used originally to encrypt

        Returns:
            The decrypted key
        """
        ...
