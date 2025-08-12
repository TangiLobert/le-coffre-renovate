import pytest

from vault_management_context.adapters.secondary.gateways import (
    FakeVaultRepository,
)
from mocks.adapters.secondary.fake_shamir_gateway import FakeShamirGateway


@pytest.fixture()
def vault_repository():
    return FakeVaultRepository()


@pytest.fixture()
def shamir_gateway():
    return FakeShamirGateway()
