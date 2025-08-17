import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from vault_management_context.application.gateways import EncryptionGateway


class AesEncryptionGateway(EncryptionGateway):
    def generate_encrypted_key(self, master_key: str) -> str:
        """Generate a random vault key and encrypt it using the master key"""
        # Generate a 32-byte (256-bit) vault key
        vault_key = get_random_bytes(32)

        # Generate a random salt for key derivation
        salt = get_random_bytes(16)

        # Derive a 256-bit key from the master key using PBKDF2
        derived_key = PBKDF2(master_key, salt, 32, count=100000)

        # Create AES cipher in GCM mode for authenticated encryption
        cipher = AES.new(derived_key, AES.MODE_GCM)

        # Encrypt the vault key
        ciphertext, auth_tag = cipher.encrypt_and_digest(vault_key)

        # Combine salt + nonce + auth_tag + ciphertext
        encrypted_data = salt + cipher.nonce + auth_tag + ciphertext

        return encrypted_data.hex()

    def decrypt_key(self, encrypted_key: str, master_key: str) -> str:
        """Decrypt a key using the master key"""
        encrypted_data = bytes.fromhex(encrypted_key)

        # Extract components from encrypted data
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:32]
        auth_tag = encrypted_data[32:48]
        ciphertext = encrypted_data[48:]

        # Derive the same key using PBKDF2
        derived_key = PBKDF2(master_key, salt, 32, count=100000)

        # Create AES cipher in GCM mode
        cipher = AES.new(derived_key, AES.MODE_GCM, nonce=nonce)

        try:
            decrypted_key = cipher.decrypt_and_verify(ciphertext, auth_tag)
            return decrypted_key.hex()
        except ValueError as e:
            raise ValueError(f"Failed to decrypt vault key: {e}") from e
