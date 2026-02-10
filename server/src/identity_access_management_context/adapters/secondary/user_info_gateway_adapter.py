from uuid import UUID

from identity_access_management_context.application.gateways import UserRepository


class UserInfoGatewayAdapter:
    """Adapter implementing the UserInfoGateway interface from Password Management context.

    This adapter allows the Password Management context to retrieve user information
    without creating a direct dependency on the IAM context.
    """

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def get_user_email(self, user_id: UUID) -> str | None:
        """Get email address for a user.

        Args:
            user_id: The ID of the user

        Returns:
            The user's email address, or None if user not found
        """
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            return None
        return user.email
