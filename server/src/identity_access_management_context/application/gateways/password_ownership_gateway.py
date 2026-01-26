from typing import Protocol
from uuid import UUID


class PasswordOwnershipGateway(Protocol):
    def group_owns_passwords(self, group_id: UUID) -> bool:
        """Check if a group owns any passwords"""
        ...
