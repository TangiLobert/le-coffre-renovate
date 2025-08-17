import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from vault_management_context.adapters.primary.api.routes import (
    get_vault_management_router,
)

from vault_management_context.adapters.primary.api.app_dependencies import (
    get_vault_repository,
    get_shamir_gateway,
)


@pytest.fixture
def client(vault_repository, shamir_gateway):
    app = FastAPI()
    app.include_router(get_vault_management_router())

    client = TestClient(app)

    client.app.dependency_overrides[get_vault_repository] = lambda: vault_repository
    client.app.dependency_overrides[get_shamir_gateway] = lambda: shamir_gateway

    return client
