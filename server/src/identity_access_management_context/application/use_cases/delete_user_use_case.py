from identity_access_management_context.application.gateways import UserRepository
from identity_access_management_context.application.commands import DeleteUserCommand
from identity_access_management_context.domain.events import UserDeletedEvent
from shared_kernel.domain.services import AdminPermissionChecker
from shared_kernel.application.gateways import DomainEventPublisher


class DeleteUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: DomainEventPublisher,
    ):
        self.user_repository = user_repository
        self.event_publisher = event_publisher

    def execute(self, command: DeleteUserCommand) -> None:
        AdminPermissionChecker().ensure_admin(command.requesting_user, "delete users")
        user_id = command.user_id

        self.user_repository.delete(user_id)

        event = UserDeletedEvent(
            user_id=user_id,
            deleted_by_user_id=command.requesting_user.user_id,
        )
        self.event_publisher.publish(event)
