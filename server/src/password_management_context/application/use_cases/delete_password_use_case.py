from uuid import UUID
from password_management_context.application.gateways import PasswordRepository
from password_management_context.domain.exceptions import PasswordNotFoundError
from shared_kernel.access_control.access_controller import AccessController
from shared_kernel.access_control.exceptions import AccessDeniedError


class DeletePasswordUseCase:
    def __init__(self, password_repository: PasswordRepository, access_controller: AccessController):
        self.password_repository = password_repository
        self.access_controller = access_controller

    def execute(self, requester_id: UUID, password_id: UUID) -> None:
        if not self.password_repository.get_by_id(password_id):
            raise PasswordNotFoundError(password_id)
        if not self.access_controller.check_delete_access(requester_id, password_id):
            raise AccessDeniedError(requester_id, password_id)
        self.password_repository.delete(password_id)
