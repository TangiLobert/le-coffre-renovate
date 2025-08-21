from typing import Optional

from password_management_context.application.gateways import PasswordRepository
from shared_kernel.encryption import EncryptionService


class CreatePasswordUseCase:
    def __init__(
        self,
        password_repository: PasswordRepository,
        encryption_service: EncryptionService,
    ):
        self.password_repository = password_repository
        self.encryption_service = encryption_service

    def execute(self, name: str, password: str, folder: Optional[str] = None):
        encrypted_value = self.encryption_service.encrypt(password)
        self.password_repository.save(name, encrypted_value, folder)
