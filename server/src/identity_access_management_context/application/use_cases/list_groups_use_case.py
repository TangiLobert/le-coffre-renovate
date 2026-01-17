from identity_access_management_context.application.gateways import GroupRepository
from identity_access_management_context.domain.entities import Group


class ListGroupsUseCase:
    def __init__(self, group_repository: GroupRepository):
        self.group_repository = group_repository

    def execute(self) -> list[Group]:
        return self.group_repository.get_all()
