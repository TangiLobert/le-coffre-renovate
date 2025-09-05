from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateAdminCommand:
    id: UUID
    username: str
    email: str
    name: str
