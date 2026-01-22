from typing import List, Dict, Any
from shared_kernel.pubsub import DomainEvent
from shared_kernel.pubsub.adapters.in_memory_event_publisher import (
    InMemoryDomainEventPublisher,
)


class InMemoryAuditLogger:
    def __init__(self, event_publisher: InMemoryDomainEventPublisher):
        self._logs: List[Dict[str, Any]] = []
        event_publisher.subscribe(DomainEvent, self._handle_event)

    def _handle_event(self, event: DomainEvent):
        self._logs.append(
            {"event_type": type(event).__name__, "payload": event.__dict__}
        )

    def get_logs(self) -> List[Dict[str, Any]]:
        return self._logs
