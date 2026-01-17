from uuid import UUID


class FakeGroupAccessGateway:
    """Fake implementation of GroupAccessGateway for testing"""

    def __init__(self):
        self._group_owners: dict[UUID, UUID] = {}  # group_id -> user_id

    def is_user_owner_of_group(self, user_id: UUID, group_id: UUID) -> bool:
        """Check if user owns the group"""
        return self._group_owners.get(group_id) == user_id

    def group_exists(self, group_id: UUID) -> bool:
        """Check if group exists"""
        return group_id in self._group_owners

    def set_group_owner(self, group_id: UUID, user_id: UUID) -> None:
        """Test helper to setup ownership"""
        self._group_owners[group_id] = user_id

    def clear(self) -> None:
        """Test helper to clear all data"""
        self._group_owners.clear()
