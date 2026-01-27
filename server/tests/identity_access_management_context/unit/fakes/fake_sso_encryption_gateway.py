from identity_access_management_context.application.gateways import (
    SsoEncryptionGateway,
)


class FakeSsoEncryptionGateway(SsoEncryptionGateway):
    def encrypt(self, plaintext: str) -> str:
        return f"encrypted({plaintext})"

    def decrypt(self, encrypted: str) -> str:
        return encrypted.replace("encrypted(", "").replace(")", "")
