from shared_kernel.domain.entities import DomainEvent


class FakeEventRepository:
    def __init__(self):
        self.events: list[DomainEvent] = []

    def append_event(self, event: DomainEvent) -> None:
        self.events.append(event)

    def list_events(self, event_types: list[str] | None = None) -> list[DomainEvent]:
        if event_types:
            return [event for event in self.events if event.event_type in event_types]
        return self.events
