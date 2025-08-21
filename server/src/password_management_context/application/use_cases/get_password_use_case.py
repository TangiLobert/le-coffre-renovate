from uuid import UUID

from password_management_context.application.gateways import PasswordRepository
from password_management_context.application.responses import PasswordResponse
from shared_kernel.encryption import EncryptionService


class GetPasswordUseCase:
    def __init__(
        self,
        password_repository: PasswordRepository,
        encryption_service: EncryptionService,
    ):
        self.password_repository = password_repository
        self.encryption_service = encryption_service

    def execute(self, password_id: UUID) -> PasswordResponse:
        password_entity = self.password_repository.get_by_id(password_id)

        decrypted_password = self.encryption_service.decrypt(
            password_entity.encrypted_value
        )

        return PasswordResponse(
            id=password_entity.id,
            name=password_entity.name,
            decrypted_password=decrypted_password,
            folder=password_entity.folder,
        )
