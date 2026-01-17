from uuid import UUID

from identity_access_management_context.application.gateways import (
    GroupRepository,
    GroupMemberRepository,
)


class GroupAccessGatewayAdapter:
    """Adapter implementing the GroupAccessGateway interface from Password Management context.

    This adapter allows the Password Management context to verify group ownership
    without creating a direct dependency on the IAM context.
    """

    def __init__(
        self,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
    ):
        self._group_repository = group_repository
        self._group_member_repository = group_member_repository

    def is_user_owner_of_group(self, user_id: UUID, group_id: UUID) -> bool:
        """Check if a user is the owner of a group.

        Args:
            user_id: The ID of the user to check
            group_id: The ID of the group to check

        Returns:
            True if the user owns the group, False otherwise
        """
        group = self._group_repository.get_by_id(group_id)
        if group is None:
            # Fallback to check personal groups
            personal_group = self._group_repository.get_by_user_id(user_id)
            if personal_group and personal_group.id == group_id:
                return True
            return False

        # For new Group entities, check membership
        return self._group_member_repository.is_owner(group_id, user_id)

    def group_exists(self, group_id: UUID) -> bool:
        """Check if a group exists.

        Args:
            group_id: The ID of the group to check

        Returns:
            True if the group exists, False otherwise
        """
        group = self._group_repository.get_by_id(group_id)
        if group is not None:
            return True

        # Fallback: check if it's a personal group
        all_personal_groups = self._group_repository.get_all_personals()
        return any(g.id == group_id for g in all_personal_groups)
