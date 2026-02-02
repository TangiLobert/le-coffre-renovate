from fastapi import APIRouter
from . import event_list_routes


def get_audit_logging_router():
    """Create and configure the audit logging router."""
    audit_logging_router = APIRouter()

    audit_logging_router.include_router(event_list_routes.router)

    return audit_logging_router
