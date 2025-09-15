from uuid import UUID

from user_management_context.application.interfaces import UserRepository
from user_management_context.application.commands import CreateUserCommand
from user_management_context.domain.entities import User
from user_management_context.domain.exceptions import AdminAlreadyExistsError


class CreateAdminUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, command: CreateUserCommand) -> UUID:
        current_admin = self.user_repository.get_admin()
        if current_admin:
            raise AdminAlreadyExistsError()

        admin = User(
            id=command.id,
            username=command.username,
            email=command.email,
            name=command.name,
            roles=["admin"],
        )

        self.user_repository.save(admin)
        return admin.id
