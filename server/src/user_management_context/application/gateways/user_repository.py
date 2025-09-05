from typing import Protocol, Optional
from uuid import UUID

from user_management_context.domain.entities import User


class UserRepository(Protocol):
    def get_by_id(self, user_id: UUID) -> Optional[User]: ...

    def save(self, user: User) -> None: ...

    def get_admin(self) -> Optional[User]: ...
