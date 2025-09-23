from typing import Protocol, Type, Callable

from pubsub import DomainEvent


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...

    def subscribe(
        self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]
    ) -> None: ...
