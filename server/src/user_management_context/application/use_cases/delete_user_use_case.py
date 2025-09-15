from user_management_context.application.interfaces import UserRepository
from user_management_context.application.commands import DeleteUserCommand
from shared_kernel.authentication import NotAdminError, AuthenticatedUser


class DeleteUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, command: DeleteUserCommand) -> None:
        self._check_admin_permission(command.requesting_user)
        user_id = command.user_id

        self.user_repository.delete(user_id)

    def _check_admin_permission(self, requesting_user: AuthenticatedUser) -> None:
        if "admin" not in requesting_user.roles:
            raise NotAdminError("Only administrators can delete users")
