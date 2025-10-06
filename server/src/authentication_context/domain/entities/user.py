from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    user_id: UUID
    email: str
    display_name: str
