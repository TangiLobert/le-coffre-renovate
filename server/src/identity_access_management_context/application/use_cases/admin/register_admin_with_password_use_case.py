from uuid import UUID

from identity_access_management_context.application.commands import (
    RegisterAdminWithPasswordCommand,
)
from identity_access_management_context.application.gateways import (
    UserPasswordRepository,
    PasswordHashingGateway,
    UserRepository,
)
from identity_access_management_context.application.services import (
    UserManagementService,
)
from identity_access_management_context.domain.entities import UserPassword
from identity_access_management_context.domain.exceptions import (
    AdminAlreadyExistsException,
)


class RegisterAdminWithPasswordUseCase:
    def __init__(
        self,
        user_password_repository: UserPasswordRepository,
        password_hashing_gateway: PasswordHashingGateway,
        user_repository: UserRepository,
    ):
        self._user_password_repository = user_password_repository
        self._password_hashing_gateway = password_hashing_gateway
        self._user_repository = user_repository

    async def execute(self, command: RegisterAdminWithPasswordCommand) -> UUID:
        # Create service instance
        user_management_service = UserManagementService(
            self._user_repository, self._password_hashing_gateway
        )

        # Check if admin can be created
        if not user_management_service.can_create_admin():
            raise AdminAlreadyExistsException("An admin account already exists")

        # Hash password and save to password repository
        password_hash = self._password_hashing_gateway.hash(command.password)
        user_password = UserPassword(
            id=command.id,
            email=command.email,
            password_hash=password_hash,
            display_name=command.display_name,
        )
        self._user_password_repository.save(user_password)

        # Create admin user via service
        user_management_service.create_admin(
            user_id=command.id,
            email=command.email,
            username=command.email.split("@")[0],
            name=command.display_name,
        )

        return user_password.id
