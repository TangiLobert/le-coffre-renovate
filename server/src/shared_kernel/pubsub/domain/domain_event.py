from datetime import datetime, UTC
from abc import ABC
from typing import Optional
from uuid import UUID


class DomainEvent(ABC):
    def __init__(
        self,
        event_id: UUID,
        occurred_on: Optional[datetime] = None,
    ) -> None:
        self.event_id = event_id
        self.occurred_on = occurred_on or datetime.now(UTC)
        self.event_type = self.__class__.__name__
