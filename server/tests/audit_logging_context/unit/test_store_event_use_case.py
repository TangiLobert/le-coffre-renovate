from uuid import uuid4
from datetime import datetime
import pytest

from shared_kernel.pubsub.domain.domain_event import DomainEvent
from audit_logging_context.application.use_cases.store_event_use_case import (
    StoreEventUseCase,
    LogRepo,
)


@pytest.fixture
def log_repo():
    return LogRepo()


@pytest.fixture
def use_case(log_repo):
    return StoreEventUseCase(log_repo)


def test_given_event_when_store_should_succeed(use_case, log_repo):
    event = DomainEvent(uuid4(), datetime.now())

    use_case.execute(event)

    assert log_repo.logs == [event]
