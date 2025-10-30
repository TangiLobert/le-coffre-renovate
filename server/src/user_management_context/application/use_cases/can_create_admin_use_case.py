from user_management_context.application.responses.can_create_admin_response import (
    CanCreateAdminResponse,
)
from user_management_context.application.interfaces import UserRepository
from user_management_context.application.services import AdminExistenceService


class CanCreateAdminUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self) -> CanCreateAdminResponse:
        admin_exists = AdminExistenceService.admin_exists(self.user_repository)
        return CanCreateAdminResponse(can_create=not admin_exists)
