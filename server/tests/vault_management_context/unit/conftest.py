import pytest

from mocks.adapters.secondary.fake_vault_repository import FakeVaultRepository
from mocks.adapters.secondary.fake_shamir_gateway import FakeShamirGateway
from mocks.adapters.secondary.fake_encryption_gateway import FakeEncryptionGateway
from mocks.adapters.secondary.fake_vault_session_gateway import FakeVaultSessionGateway


@pytest.fixture()
def vault_repository():
    return FakeVaultRepository()


@pytest.fixture()
def shamir_gateway():
    return FakeShamirGateway()


@pytest.fixture()
def encryption_gateway():
    return FakeEncryptionGateway()


@pytest.fixture()
def vault_session_gateway():
    return FakeVaultSessionGateway()
