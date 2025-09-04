from uuid import UUID

from authentication_context.application.commands import CreateAdminAccountCommand
from authentication_context.application.gateways import (
    AdminRepository,
    PasswordHashingGateway,
)
from authentication_context.domain.entities import AdminAccount
from authentication_context.domain.exceptions import AdminAlreadyExistsException


class CreateAdminAccountUseCase:
    def __init__(
        self,
        admin_repository: AdminRepository,
        password_hashing_gateway: PasswordHashingGateway,
    ):
        self._admin_repository = admin_repository
        self._password_hashing_gateway = password_hashing_gateway

    def execute(self, command: CreateAdminAccountCommand) -> UUID:
        if self._admin_repository.exists_any():
            raise AdminAlreadyExistsException("An admin account already exists")

        password_hash = self._password_hashing_gateway.hash_password(command.password)

        admin = AdminAccount(
            id=command.id,
            email=command.email,
            password_hash=password_hash,
            display_name=command.display_name,
        )

        self._admin_repository.save(admin)
        return admin.id
