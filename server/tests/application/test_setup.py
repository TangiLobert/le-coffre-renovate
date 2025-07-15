import pytest


from src.application.usecase.setup_master_password import SetupMasterPasswordUseCase
from src.domain.setup_info import SetupInfo


class MockSetupStore:
    def __init__(self):
        self._setup_info = None

    def get_setup(self):
        return self._setup_info

    def mark_setup(self, setup_info):
        self._setup_info = setup_info


@pytest.fixture()
def setup_use_case():
    store = MockSetupStore()
    return SetupMasterPasswordUseCase(store)


def test_given_a_master_password_when_setup_then_application_is_marked_as_setup(
    setup_use_case,
):
    password = "SuperSecret123!"
    setup_status = setup_use_case.execute(password)
    assert setup_status == True


def test_given_master_password_already_set_when_setup_called_again_then_should_fail(
    setup_use_case,
):
    password = "SuperSecret123!"
    setup_use_case.execute(password)
    result = setup_use_case.execute("AnotherPassword!")
    assert result == False
