from fastapi import Depends
from starlette.requests import Request

from password_management_context.application.use_cases import (
    CreatePasswordUseCase,
    GetPasswordUseCase,
    UpdatePasswordUseCase,
    ListPasswordsUseCase,
    DeletePasswordUseCase,
)
from password_management_context.application.gateways import PasswordRepository
from shared_kernel.encryption import EncryptionService
from shared_kernel.access_control import AccessController
from rights_access_context.application.use_cases import (
    ShareAccessUseCase,
    UnshareAccessUseCase,
)
from rights_access_context.application.gateways import RightsRepository


def get_password_repository(request: Request) -> PasswordRepository:
    return request.app.state.password_repository


def get_encryption_service(request: Request) -> EncryptionService:
    return request.app.state.encryption_service


def get_access_controller(request: Request) -> AccessController:
    return request.app.state.access_controller


def get_create_password_usecase(
    password_repository: PasswordRepository = Depends(get_password_repository),
    encryption_service: EncryptionService = Depends(get_encryption_service),
    access_controller: AccessController = Depends(get_access_controller),
):
    return CreatePasswordUseCase(
        password_repository, encryption_service, access_controller
    )


def get_get_password_usecase(
    password_repository: PasswordRepository = Depends(get_password_repository),
    encryption_service: EncryptionService = Depends(get_encryption_service),
    access_controller: AccessController = Depends(get_access_controller),
):
    return GetPasswordUseCase(
        password_repository, encryption_service, access_controller
    )


def get_update_password_usecase(
    password_repository: PasswordRepository = Depends(get_password_repository),
    encryption_service: EncryptionService = Depends(get_encryption_service),
    access_controller: AccessController = Depends(get_access_controller),
):
    return UpdatePasswordUseCase(
        password_repository, encryption_service, access_controller
    )


def get_list_passwords_usecase(
    password_repository: PasswordRepository = Depends(get_password_repository),
    encryption_service: EncryptionService = Depends(get_encryption_service),
    access_controller: AccessController = Depends(get_access_controller),
):
    return ListPasswordsUseCase(
        password_repository, encryption_service, access_controller
    )


def get_delete_password_usecase(
    password_repository: PasswordRepository = Depends(get_password_repository),
    access_controller: AccessController = Depends(get_access_controller),
):
    return DeletePasswordUseCase(password_repository, access_controller)


def get_rights_repository(request: Request) -> RightsRepository:
    return request.app.state.rights_repository


def get_share_access_usecase(
    rights_repository: RightsRepository = Depends(get_rights_repository),
):
    return ShareAccessUseCase(rights_repository)


def get_unshare_access_usecase(
    rights_repository: RightsRepository = Depends(get_rights_repository),
):
    return UnshareAccessUseCase(rights_repository)
