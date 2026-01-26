from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteGroupCommand:
    requester_id: UUID
    group_id: UUID
