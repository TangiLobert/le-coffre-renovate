from dataclasses import dataclass
from typing import List
from uuid import UUID


@dataclass
class AuthenticatedUser:
    user_id: UUID
    roles: list[str]
