import pytest
from uuid import UUID

from password_management_context.application.use_cases import GetPasswordUseCase
from password_management_context.adapters.secondary.gateways import (
    InMemoryPasswordRepository,
)
from password_management_context.domain.exceptions import PasswordNotFoundError
from password_management_context.domain.entities import Password


@pytest.fixture
def use_case(password_repository, encryption_service):
    return GetPasswordUseCase(password_repository, encryption_service)


def test_should_return_decrypted_password_when_password_exists(
    use_case: GetPasswordUseCase, password_repository: InMemoryPasswordRepository
):
    uuid = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    name = "name"
    folder = "folder"
    encrypted_password = "encrypted(secret123)"
    expected_decrypted = "secret123"

    password = Password(
        id=uuid,
        name=name,
        encrypted_value=encrypted_password,
        folder=folder,
    )
    password_repository.save(password)

    result = use_case.execute(uuid)

    assert result.id == uuid
    assert result.name == name
    assert result.folder == folder
    assert result.decrypted_password == expected_decrypted


def test_should_raise_exception_when_password_not_found(use_case: GetPasswordUseCase):
    non_existent_password_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")

    with pytest.raises(PasswordNotFoundError):
        use_case.execute(non_existent_password_id)
