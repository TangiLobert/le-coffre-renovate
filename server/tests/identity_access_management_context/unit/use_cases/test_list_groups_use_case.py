import pytest
from uuid import uuid4

from identity_access_management_context.application.use_cases import ListGroupsUseCase
from identity_access_management_context.domain.entities import Group


@pytest.fixture
def use_case(group_repository):
    return ListGroupsUseCase(group_repository)


def test_given_no_groups_when_listings_groups_should_return_empty_list(use_case):
    result = use_case.execute()
    assert result == []


def test_given_groups_when_listing_groups_should_return_list_of_groups(
    use_case, group_repository
):
    group1 = uuid4()
    group2 = uuid4()

    group_repository.save_group(Group(id=group1, name="Group 1", is_personal=False))
    group_repository.save_group(Group(id=group2, name="Group 2", is_personal=False))

    result = use_case.execute()

    assert result == [
        Group(id=group1, name="Group 1", is_personal=False),
        Group(id=group2, name="Group 2", is_personal=False),
    ]
