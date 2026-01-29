from dataclasses import dataclass
from uuid import UUID


@dataclass
class UpdateGroupCommand:
    requester_id: UUID
    group_id: UUID
    name: str
