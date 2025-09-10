from user_management_context.application.interfaces import UserRepository
from uuid import UUID
from typing import Optional
from user_management_context.domain.entities import User


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(
        self, user_id: Optional[UUID] = None, user_email: Optional[str] = None
    ) -> User:
        if user_id is not None:
            return self.user_repository.get_by_id(user_id)
        if user_email is not None:
            return self.user_repository.get_by_email(user_email)

        raise ValueError("Either user_id or user_email must be provided.")
