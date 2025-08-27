from uuid import UUID
from password_management_context.application.gateways import PasswordRepository
from password_management_context.domain.entities import Password
from password_management_context.application.commands import CreatePasswordCommand
from shared_kernel.encryption import EncryptionService


class UpdatePasswordUseCase:
  def __init__(self, password_repository: PasswordRepository, encryption_service: EncryptionService):
    self.password_repository = password_repository
    self.encryption_service = encryption_service

  def execute(self, new_password: CreatePasswordCommand) -> None:
    encrypted_value = self.encryption_service.encrypt(new_password.decrypted_password)

    updated_password = Password.create(
            id=new_password.id,
            name=new_password.name,
            encrypted_value=encrypted_value,
            folder=new_password.folder,
        )

    self.password_repository.update(updated_password)
