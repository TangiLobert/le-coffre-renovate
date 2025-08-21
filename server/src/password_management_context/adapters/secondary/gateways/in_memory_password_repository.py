from typing import Dict
from uuid import UUID

from password_management_context.application.gateways import PasswordRepository
from password_management_context.domain.entities import Password
from password_management_context.domain.exceptions import PasswordNotFoundError


class InMemoryPasswordRepository(PasswordRepository):
    def __init__(self):
        self.storage: Dict[UUID, Password] = {}

    def save(self, password: Password) -> None:
        self.storage[password.id] = password

    def get_by_id(self, id: UUID) -> Password:
        if id not in self.storage:
            raise PasswordNotFoundError(id)
        return self.storage[id]
