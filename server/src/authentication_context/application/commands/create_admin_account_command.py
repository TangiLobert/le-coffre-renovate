from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateAdminAccountCommand:
    id: UUID
    email: str
    password: str
    display_name: str
