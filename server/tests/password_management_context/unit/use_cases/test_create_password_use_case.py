import pytest
from uuid import UUID

from password_management_context.application.gateways import PasswordRepository
from password_management_context.application.commands import CreatePasswordCommand
from password_management_context.application.use_cases import CreatePasswordUseCase

from tests.fakes.fake_access_controller import (
    FakeAccessController,
)


ANY_PASSWORD = "any_password"


@pytest.fixture
def use_case(password_repository, encryption_service, access_controller):
    return CreatePasswordUseCase(
        password_repository, encryption_service, access_controller
    )


def test_should_create_password_with_uuid_and_store_encrypted(
    use_case: CreatePasswordUseCase, password_repository: PasswordRepository
):
    uuid = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    user_id = UUID("1d742e0e-bb76-4728-83ef-8d546d7c62e6")
    name = "name"
    decrypted_password = ANY_PASSWORD
    expected_encrypted = "encrypted(" + decrypted_password + ")"

    command = CreatePasswordCommand(
        user_id=user_id, id=uuid, name=name, decrypted_password=decrypted_password
    )

    password_id = use_case.execute(command)

    assert password_id == uuid

    saved_password = password_repository.get_by_id(password_id)
    assert saved_password.id == uuid
    assert saved_password.name == name
    assert saved_password.encrypted_value == expected_encrypted


def test_should_create_password_in_folder_with_encrypted_value(
    use_case: CreatePasswordUseCase, password_repository: PasswordRepository
):
    uuid = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    user_id = UUID("1d742e0e-bb76-4728-83ef-8d546d7c62e6")
    folder = "Work"
    name = "Slack"
    decrypted_password = ANY_PASSWORD
    expected_encrypted = "encrypted(" + decrypted_password + ")"

    command = CreatePasswordCommand(
        user_id=user_id,
        id=uuid,
        name=name,
        decrypted_password=decrypted_password,
        folder=folder,
    )

    password_id = use_case.execute(command)

    assert password_id == uuid
    saved_password = password_repository.get_by_id(password_id)
    assert saved_password.name == name
    assert saved_password.folder == folder
    assert saved_password.encrypted_value == expected_encrypted


def test_should_create_password_in_default_folder_when_not_given(
    use_case: CreatePasswordUseCase, password_repository: PasswordRepository
):
    uuid = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    user_id = UUID("1d742e0e-bb76-4728-83ef-8d546d7c62e6")
    name = "Slack"
    decrypted_password = ANY_PASSWORD

    command = CreatePasswordCommand(
        user_id=user_id,
        id=uuid,
        name=name,
        decrypted_password=decrypted_password,
    )

    password_id = use_case.execute(command)

    assert password_id == uuid
    saved_password = password_repository.get_by_id(password_id)
    assert saved_password.folder == "default"


def test_should_grant_access_to_user_when_creating_password(
    use_case: CreatePasswordUseCase, access_controller: FakeAccessController
):
    uuid = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    user_id = UUID("1d742e0e-bb76-4728-83ef-8d546d7c62e6")
    name = "name"
    decrypted_password = ANY_PASSWORD

    command = CreatePasswordCommand(
        user_id=user_id, id=uuid, name=name, decrypted_password=decrypted_password
    )

    use_case.execute(command)

    assert access_controller.check_access(user_id, uuid)
