from shared_kernel.pubsub import DomainEvent


class AuditLogEvent(DomainEvent):
    def __init__(self, event_type: str, payload: dict):
        self.event_type = event_type
        self.payload = payload
