from shared_kernel.domain.entities import DomainEvent, AuthenticatedUser
from shared_kernel.domain.services import AdminPermissionChecker


class ListEventUseCase:
    def __init__(self, event_repository):
        self.event_repository = event_repository

    def execute(self, requesting_user: AuthenticatedUser) -> list[DomainEvent]:
        """List all audit events. Only administrators can access audit logs."""
        AdminPermissionChecker.ensure_admin(requesting_user, "view audit event logs")
        return self.event_repository.list_events()
