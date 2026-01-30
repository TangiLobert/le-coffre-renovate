from fastapi import Depends
from starlette.requests import Request

from audit_logging_context.application.gateways import EventRepository
from audit_logging_context.application.use_cases import ListEventUseCase


def get_event_repository(request: Request) -> EventRepository:
    """Get event repository from app state."""
    return request.app.state.event_repository


def get_list_event_usecase(
    event_repository: EventRepository = Depends(get_event_repository),
) -> ListEventUseCase:
    """Factory for ListEventUseCase with dependencies."""
    return ListEventUseCase(event_repository)
