from shared_kernel.domain.entities import DomainEvent


class ListEventUseCase:
    def __init__(self, event_repository):
        self.event_repository = event_repository

    def execute(self) -> list[DomainEvent]:
        return self.event_repository.list_events()
