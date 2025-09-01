from uuid import UUID

from rights_access_context.application.gateways import (
    RightsRepository,
)
from rights_access_context.application.responses import AccessResult
from rights_access_context.domain.value_objects import Permission

class CheckAccessUseCase:
    def __init__(self, rights_repository: RightsRepository):
        self.rights_repository = rights_repository

    def execute(self, user_id: UUID, resource_id: UUID, permission: Permission = Permission.READ) -> AccessResult:
        has_permission = self.rights_repository.has_permission(user_id, resource_id, permission)
        return AccessResult(granted=has_permission)
