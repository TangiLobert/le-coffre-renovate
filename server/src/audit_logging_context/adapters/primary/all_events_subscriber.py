from typing import Callable
from sqlmodel import Session
from audit_logging_context.application.use_cases.store_event_use_case import (
    StoreEventUseCase,
)
from audit_logging_context.application.commands import StoreEventCommand
from audit_logging_context.adapters.secondary.sql import SqlEventRepository


class AllEventsSubscriber:
    def __init__(self, session_maker: Callable[[], Session]) -> None:
        self.session_maker = session_maker

    def __call__(self, event) -> None:
        with self.session_maker() as session:
            event_repository = SqlEventRepository(session)
            store_event_usecase = StoreEventUseCase(event_repository)
            command = StoreEventCommand(event=event)
            store_event_usecase.execute(command)
