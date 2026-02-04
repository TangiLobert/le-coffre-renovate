from fastapi import Depends
from starlette.requests import Request
from sqlmodel import Session

from audit_logging_context.application.gateways import EventRepository
from audit_logging_context.application.use_cases import ListEventUseCase
from audit_logging_context.adapters.secondary.sql import SqlEventRepository
from shared_kernel.adapters.primary.dependencies import get_session


def get_event_repository(session: Session = Depends(get_session)) -> EventRepository:
    """Get event repository with session."""
    return SqlEventRepository(session)


def get_list_event_usecase(
    event_repository: EventRepository = Depends(get_event_repository),
) -> ListEventUseCase:
    """Factory for ListEventUseCase with dependencies."""
    return ListEventUseCase(event_repository)
