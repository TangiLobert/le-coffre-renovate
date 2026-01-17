from typing import Protocol

from identity_access_management_context.domain.entities import PersonalGroup


class GroupRepository(Protocol):
    def save_personal_group(self, group: PersonalGroup) -> None:
        """Save a personal group to the repository."""
        ...

    def get_all(self) -> list[PersonalGroup]:
        """Get all personal groups."""
        ...
