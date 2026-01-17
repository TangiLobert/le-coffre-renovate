from uuid import UUID

from identity_access_management_context.application.gateways import GroupRepository
from identity_access_management_context.domain.entities import Group
from identity_access_management_context.domain.exceptions import GroupNotFoundException


class GetGroupUseCase:
    def __init__(self, group_repository: GroupRepository):
        self.group_repository = group_repository

    def execute(self, group_id: UUID) -> Group:
        group = self.group_repository.get_by_id(group_id)
        if not group:
            raise GroupNotFoundException(group_id)

        return group
