from identity_access_management_context.application.commands import (
    UpdateGroupCommand,
)
from identity_access_management_context.application.gateways import (
    GroupRepository,
    GroupMemberRepository,
)
from identity_access_management_context.domain.exceptions import (
    GroupNotFoundException,
    UserNotOwnerOfGroupException,
    CannotModifyPersonalGroupException,
)
from shared_kernel.domain.services import AdminPermissionChecker


class UpdateGroupUseCase:
    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository

    def execute(self, command: UpdateGroupCommand) -> None:
        group = self.group_repository.get_by_id(command.group_id)
        if group is None:
            raise GroupNotFoundException(command.group_id)

        if group.is_personal:
            raise CannotModifyPersonalGroupException(command.group_id)

        if not self.group_member_repository.is_owner(
            command.group_id, command.requesting_user.user_id
        ) and not AdminPermissionChecker().is_admin(command.requesting_user):
            raise UserNotOwnerOfGroupException(
                command.requesting_user.user_id, command.group_id
            )

        group.name = command.name
        self.group_repository.save_group(group)
