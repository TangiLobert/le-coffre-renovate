from uuid import UUID


class FakePasswordOwnershipGateway:
    def __init__(self):
        self._groups_with_passwords: set[UUID] = set()

    def group_owns_passwords(self, group_id: UUID) -> bool:
        return group_id in self._groups_with_passwords

    def add_group_with_passwords(self, group_id: UUID) -> None:
        self._groups_with_passwords.add(group_id)

    def remove_group_passwords(self, group_id: UUID) -> None:
        self._groups_with_passwords.discard(group_id)
