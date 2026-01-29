from typing import Protocol

from shared_kernel.domain.entities import DomainEvent


class EventRepository(Protocol):
    def append_event(self, event: DomainEvent) -> None: ...
    def list_events(self) -> list[DomainEvent]: ...
