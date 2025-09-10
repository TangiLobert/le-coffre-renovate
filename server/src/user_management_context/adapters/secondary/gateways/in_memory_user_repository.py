from typing import Optional
from uuid import UUID
from user_management_context.application.gateways import UserRepository
from user_management_context.domain.entities import User
from user_management_context.domain.exceptions import UserNotFoundError, UserAlreadyExistsError


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.storage: dict[UUID, User] = {}

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        if user_id not in self.storage:
            raise UserNotFoundError(user_id)
        return self.storage.get(user_id)

    def save(self, user: User) -> None:
        if any(u.username == user.username for u in self.storage.values()):
            raise UserAlreadyExistsError(user.username)
        self.storage[user.id] = user
