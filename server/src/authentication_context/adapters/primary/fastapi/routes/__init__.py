from fastapi import APIRouter
from . import (
    register_admin_with_password_route,
    admin_login_route,
    get_sso_url_route,
    configure_sso_provider_route,
    sso_callback_route,
)


def get_authentication_router():
    authentication_router = APIRouter()

    authentication_router.include_router(register_admin_with_password_route.router)
    authentication_router.include_router(admin_login_route.router)
    authentication_router.include_router(get_sso_url_route.router)
    authentication_router.include_router(configure_sso_provider_route.router)
    authentication_router.include_router(sso_callback_route.router)

    return authentication_router
