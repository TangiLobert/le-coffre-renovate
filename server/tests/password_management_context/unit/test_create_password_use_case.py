import pytest

from password_management_context.application.use_cases import CreatePasswordUseCase
from password_management_context.adapters.secondary.gateways import (
    InMemoryPasswordRepository,
)
from mocks import FakeEncryptionService


@pytest.fixture
def password_repository():
    return InMemoryPasswordRepository()


@pytest.fixture
def encryption_service():
    return FakeEncryptionService()


@pytest.fixture
def use_case(password_repository, encryption_service):
    return CreatePasswordUseCase(password_repository, encryption_service)


def test_should_store_a_given_password_encrypted(
    use_case: CreatePasswordUseCase, password_repository
):
    name = "Name"
    value = "Dummy_Password"
    encrypted_value = "encrypted(Dummy_Password)"

    use_case.execute(name=name, password=value)

    assert password_repository.get(name) == encrypted_value


def test_should_store_in_a_folder_a_given_password_encrypted(
    use_case: CreatePasswordUseCase, password_repository
):
    folder = "folder"
    name = "Name"
    value = "Dummy_Password"

    encrypted_value = "encrypted(Dummy_Password)"

    use_case.execute(
        folder=folder,
        name=name,
        password=value,
    )

    assert password_repository.get(name, folder) == encrypted_value
