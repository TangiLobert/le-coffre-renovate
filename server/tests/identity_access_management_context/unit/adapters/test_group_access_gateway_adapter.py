import pytest
from uuid import uuid4

from identity_access_management_context.adapters.secondary.group_access_gateway_adapter import (
    GroupAccessGatewayAdapter,
)
from tests.identity_access_management_context.unit.fakes.fake_group_repository import (
    FakeGroupRepository,
)
from identity_access_management_context.domain.entities import PersonalGroup


@pytest.fixture
def group_repository():
    return FakeGroupRepository()


@pytest.fixture
def adapter(group_repository):
    return GroupAccessGatewayAdapter(group_repository)


def test_should_return_true_when_user_owns_group(adapter, group_repository):
    user_id = uuid4()
    group_id = uuid4()
    group = PersonalGroup(id=group_id, name="Test Group", user_id=user_id)
    group_repository.save_personal_group(group)

    result = adapter.is_user_owner_of_group(user_id, group_id)

    assert result is True


def test_should_return_false_when_user_does_not_own_group(adapter, group_repository):
    user_id = uuid4()
    other_user_id = uuid4()
    group_id = uuid4()
    group = PersonalGroup(id=group_id, name="Test Group", user_id=other_user_id)
    group_repository.save_personal_group(group)

    result = adapter.is_user_owner_of_group(user_id, group_id)

    assert result is False


def test_should_return_false_when_group_does_not_exist(adapter):
    user_id = uuid4()
    nonexistent_group_id = uuid4()

    result = adapter.is_user_owner_of_group(user_id, nonexistent_group_id)

    assert result is False


def test_should_return_true_when_group_exists(adapter, group_repository):
    user_id = uuid4()
    group_id = uuid4()
    group = PersonalGroup(id=group_id, name="Test Group", user_id=user_id)
    group_repository.save_personal_group(group)

    result = adapter.group_exists(group_id)

    assert result is True


def test_should_return_false_when_group_does_not_exist_for_exists_check(adapter):
    nonexistent_group_id = uuid4()

    result = adapter.group_exists(nonexistent_group_id)

    assert result is False
