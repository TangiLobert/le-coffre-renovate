from rights_access_context.application.commands import UnshareResourceCommand
from rights_access_context.domain.exceptions import (
    PermissionDeniedError,
    CannotUnshareWithOwnerError,
)


class UnshareAccessUseCase:
    def __init__(self, rights_repository):
        self.rights_repository = rights_repository

    def execute(self, command: UnshareResourceCommand):
        if not self.rights_repository.is_owner(
            command.owner_id, command.resource_id
        ):
            raise PermissionDeniedError(command.owner_id, command.resource_id)
        
        if self.rights_repository.is_owner(command.user_id, command.resource_id):
            raise CannotUnshareWithOwnerError(
                command.user_id, command.resource_id
            )
        
        self.rights_repository.remove_permission(command.user_id, command.resource_id)
