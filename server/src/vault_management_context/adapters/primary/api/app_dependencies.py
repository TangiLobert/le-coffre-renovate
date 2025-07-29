from fastapi import Depends
from starlette.requests import Request

from src.vault_management_context.business_logic.use_cases import (
    CreateVaultUseCase,
)
from src.vault_management_context.business_logic.gateways import (
    VaultRepository,
    ShamirGateway,
)


def get_vault_repository(request: Request) -> VaultRepository:
    return request.app.state.vault_repository


def get_shamir_gateway(request: Request) -> ShamirGateway:
    return request.app.state.shamir_gateway


def get_create_vault_usecase(
    vault_repository=Depends(get_vault_repository),
    shamir_gateway=Depends(get_shamir_gateway),
):
    return CreateVaultUseCase(vault_repository, shamir_gateway)
