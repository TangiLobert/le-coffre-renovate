import pytest
from uuid import UUID

from rights_access_context.application.use_cases import (
    CheckAccessUseCase,
)
from ..mocks import FakeRightsRepository
from rights_access_context.domain.value_objects import Permission

# Test data constants
USER_ID = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
RESOURCE_ID = UUID("e0e2eb69-5d6b-4500-947a-6636c8755b3f")

@pytest.fixture()
def use_case(rights_repository: FakeRightsRepository):
    return CheckAccessUseCase(rights_repository)


def test_given_owned_resource_when_reading_should_grant_access(
    use_case: CheckAccessUseCase, rights_repository: FakeRightsRepository
):
    user_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    resource_id = UUID("e0e2eb69-5d6b-4500-947a-6636c8755b3f")

    rights_repository.add_permission(user_id, resource_id, Permission.READ)

    result = use_case.execute(user_id, resource_id, Permission.READ)

    assert result.granted is True


def test_given_not_owned_resource_when_reading_should_deny_access(
    use_case: CheckAccessUseCase,
):
    user_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    resource_id = UUID("e0e2eb69-5d6b-4500-947a-6636c8755b3f")

    result = use_case.execute(user_id, resource_id)

    assert result.granted is False

@pytest.mark.parametrize("permission", [Permission.READ, Permission.UPDATE, Permission.DELETE])
def test_should_grant_access_when_user_has_required_permission(use_case, rights_repository, permission):
    # ARRANGE
    rights_repository.add_permission(USER_ID, RESOURCE_ID, permission)

    # ACT
    result = use_case.execute(USER_ID, RESOURCE_ID, permission)

    # ASSERT
    assert result.granted is True


@pytest.mark.parametrize("granted_permission, requested_permission", [
    (Permission.READ, Permission.UPDATE),
    (Permission.READ, Permission.DELETE),
    (Permission.UPDATE, Permission.DELETE),
])
def test_should_deny_access_when_user_has_insufficient_permission(
    use_case, rights_repository, granted_permission, requested_permission
):
    # ARRANGE
    rights_repository.add_permission(USER_ID, RESOURCE_ID, granted_permission)

    # ACT
    result = use_case.execute(USER_ID, RESOURCE_ID, requested_permission)

    # ASSERT
    assert result.granted is False
