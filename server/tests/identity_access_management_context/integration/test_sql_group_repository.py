import pytest
import tempfile
import os
from uuid import uuid4
from sqlmodel import create_engine, Session, SQLModel

from identity_access_management_context.adapters.secondary.sql.sql_group_repository import (
    SqlGroupRepository,
)
from identity_access_management_context.domain.entities import PersonalGroup


@pytest.fixture(scope="function")
def engine():
    """Create a temporary database engine for testing"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)

    yield engine

    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture(scope="function")
def session(engine):
    """Create a new database session for a test"""
    with Session(engine) as session:
        yield session


@pytest.fixture
def sql_group_repository(session):
    return SqlGroupRepository(session)


def test_given_personal_group_when_saving_then_group_is_stored(sql_group_repository):
    # Given
    group_id = uuid4()
    user_id = uuid4()
    name = "testuser's Personal Group"
    personal_group = PersonalGroup(id=group_id, name=name, user_id=user_id)

    # When
    sql_group_repository.save_personal_group(personal_group)

    # Then
    retrieved_group = sql_group_repository.get_by_id(group_id)
    assert retrieved_group is not None
    assert retrieved_group.id == group_id
    assert retrieved_group.name == name
    assert retrieved_group.user_id == user_id


def test_given_personal_group_when_getting_by_user_id_then_group_is_retrieved(
    sql_group_repository,
):
    # Given
    group_id = uuid4()
    user_id = uuid4()
    name = "testuser's Personal Group"
    personal_group = PersonalGroup(id=group_id, name=name, user_id=user_id)
    sql_group_repository.save_personal_group(personal_group)

    # When
    retrieved_group = sql_group_repository.get_by_user_id(user_id)

    # Then
    assert retrieved_group is not None
    assert retrieved_group.id == group_id
    assert retrieved_group.name == name
    assert retrieved_group.user_id == user_id


def test_given_no_group_when_getting_by_user_id_then_returns_none(sql_group_repository):
    # Given
    non_existent_user_id = uuid4()

    # When
    retrieved_group = sql_group_repository.get_by_user_id(non_existent_user_id)

    # Then
    assert retrieved_group is None


def test_given_multiple_groups_when_getting_all_then_all_groups_are_retrieved(
    sql_group_repository,
):
    # Given
    group1_id = uuid4()
    user1_id = uuid4()
    group1 = PersonalGroup(
        id=group1_id, name="User1's Personal Group", user_id=user1_id
    )

    group2_id = uuid4()
    user2_id = uuid4()
    group2 = PersonalGroup(
        id=group2_id, name="User2's Personal Group", user_id=user2_id
    )

    sql_group_repository.save_personal_group(group1)
    sql_group_repository.save_personal_group(group2)

    # When
    all_groups = sql_group_repository.get_all()

    # Then
    assert len(all_groups) == 2
    assert any(g.id == group1_id for g in all_groups)
    assert any(g.id == group2_id for g in all_groups)


def test_given_no_groups_when_getting_all_then_returns_empty_list(sql_group_repository):
    # Given / When
    all_groups = sql_group_repository.get_all()

    # Then
    assert all_groups == []
