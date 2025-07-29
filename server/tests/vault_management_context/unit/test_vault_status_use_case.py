import pytest

from src.vault_management_context.business_logic.gateways import (
    VaultRepository,
)
from src.vault_management_context.business_logic.use_cases import VaultStatusUseCase
from src.vault_management_context.business_logic.models.value_objects import Vault
from tests.vault_management_context.fixtures import vault_repository


@pytest.fixture()
def use_case(vault_repository):
    return VaultStatusUseCase(vault_repository)


def test_should_fail_when_no_status_exists(use_case: VaultStatusUseCase):
    status_existing = use_case.execute()

    assert status_existing is False


def test_should_succeed_when_status_exists(
    vault_repository: VaultRepository, use_case: VaultStatusUseCase
):
    vault_repository.save(Vault(3, 2, []))
    status_existing = use_case.execute()

    assert status_existing is True
