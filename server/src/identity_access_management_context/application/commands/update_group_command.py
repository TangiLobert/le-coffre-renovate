from dataclasses import dataclass
from uuid import UUID

from shared_kernel.domain.entities import AuthenticatedUser


@dataclass
class UpdateGroupCommand:
    requesting_user: AuthenticatedUser
    group_id: UUID
    name: str
