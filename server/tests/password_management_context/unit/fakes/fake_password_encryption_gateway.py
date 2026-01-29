from password_management_context.application.gateways import PasswordEncryptionGateway


class FakePasswordEncryptionGateway(PasswordEncryptionGateway):
    def encrypt(self, password: str) -> str:
        return f"encrypted({password})"

    def decrypt(self, ciphertext: str) -> str:
        return ciphertext.replace("encrypted(", "").replace(")", "")
