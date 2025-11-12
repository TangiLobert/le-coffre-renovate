from uuid import UUID
import pytest
from rights_access_context.application.use_cases import UnshareAccessUseCase
from ..fakes import FakeRightsRepository
from rights_access_context.application.commands import UnshareResourceCommand
from rights_access_context.domain.exceptions import (
    PermissionDeniedError,
    CannotUnshareWithOwnerError,
)
from rights_access_context.domain.value_objects import Permission


@pytest.fixture()
def use_case(rights_repository: FakeRightsRepository):
    return UnshareAccessUseCase(rights_repository)


def test_given_owner_when_unsharing_from_user_with_read_access_should_revoke_access(
    use_case: UnshareAccessUseCase, rights_repository: FakeRightsRepository
):
    # Arrange: Given an owner and a user with READ access
    owner_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    resource_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e7")
    user_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e6")
    rights_repository.set_owner(owner_id, resource_id)
    rights_repository.add_permission(user_id, resource_id, Permission.READ)

    # Act: When owner unshares the resource
    use_case.execute(UnshareResourceCommand(owner_id, user_id, resource_id))

    # Assert: Then the user should no longer have READ access
    assert rights_repository.has_permission(user_id, resource_id, Permission.READ) is False


def test_given_non_owner_when_unsharing_should_fail(
    use_case: UnshareAccessUseCase, rights_repository: FakeRightsRepository
):
    # Arrange: Given an owner, a user with READ access, and a non-owner with UPDATE permission
    owner_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    resource_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e7")
    user_with_read_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e6")
    non_owner_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e8")
    
    rights_repository.set_owner(owner_id, resource_id)
    rights_repository.add_permission(user_with_read_id, resource_id, Permission.READ)
    rights_repository.add_permission(non_owner_id, resource_id, Permission.UPDATE)

    # Act & Assert: When non-owner tries to unshare, then should fail
    with pytest.raises(PermissionDeniedError):
        use_case.execute(UnshareResourceCommand(non_owner_id, user_with_read_id, resource_id))
    
    # Assert: User with READ access should still have access
    assert rights_repository.has_permission(user_with_read_id, resource_id, Permission.READ) is True


def test_given_owner_when_unsharing_from_another_owner_should_fail(
    use_case: UnshareAccessUseCase, rights_repository: FakeRightsRepository
):
    # Arrange: Given two owners of the same resource
    owner_a_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    owner_b_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e6")
    resource_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e7")
    
    rights_repository.set_owner(owner_a_id, resource_id)
    rights_repository.set_owner(owner_b_id, resource_id)

    # Act & Assert: When one owner tries to unshare with another owner, then should fail
    with pytest.raises(CannotUnshareWithOwnerError):
        use_case.execute(UnshareResourceCommand(owner_a_id, owner_b_id, resource_id))


def test_given_owner_when_unsharing_from_user_without_access_should_succeed(
    use_case: UnshareAccessUseCase, rights_repository: FakeRightsRepository
):
    # Arrange: Given an owner and a user with NO access to the resource
    owner_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    resource_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e7")
    user_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e6")
    rights_repository.set_owner(owner_id, resource_id)

    # Act: When owner unshares with user who has no access (idempotent operation)
    use_case.execute(UnshareResourceCommand(owner_id, user_id, resource_id))

    # Assert: Then operation should succeed and user still has no access
    assert rights_repository.has_permission(user_id, resource_id, Permission.READ) is False
