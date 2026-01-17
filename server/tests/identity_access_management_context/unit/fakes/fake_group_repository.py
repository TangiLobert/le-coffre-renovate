from typing import Dict
from uuid import UUID

from identity_access_management_context.domain.entities import PersonalGroup


class FakeGroupRepository:
    def __init__(self):
        self._groups: Dict[UUID, PersonalGroup] = {}

    def save_personal_group(self, group: PersonalGroup) -> None:
        self._groups[group.id] = group

    def get_by_id(self, group_id: UUID) -> PersonalGroup | None:
        return self._groups.get(group_id)

    def get_by_user_id(self, user_id: UUID) -> PersonalGroup | None:
        for group in self._groups.values():
            if group.user_id == user_id:
                return group
        return None

    def get_all(self) -> list[PersonalGroup]:
        return list(self._groups.values())

    def clear(self) -> None:
        self._groups.clear()
