from fastapi import APIRouter
from . import user_get_routes


def get_user_management_router():
    user_management_router = APIRouter()

    user_management_router.include_router(user_get_routes.router)

    return user_management_router
