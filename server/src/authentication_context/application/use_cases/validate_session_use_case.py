from authentication_context.application.responses import ValidateSessionResponse
from authentication_context.application.gateways import (
    SessionRepository,
    JWTTokenGateway,
)
from authentication_context.domain.exceptions import InvalidSessionException


class ValidateSessionUseCase:
    def __init__(
        self,
        session_repository: SessionRepository,
        jwt_token_gateway: JWTTokenGateway,
    ):
        self._session_repository = session_repository
        self._jwt_token_gateway = jwt_token_gateway

    async def execute(self, jwt_token: str) -> ValidateSessionResponse:
        token_claims = await self._jwt_token_gateway.validate_token(jwt_token)
        if not token_claims:
            raise InvalidSessionException("Invalid JWT token")

        session = self._session_repository.get_by_token(jwt_token)
        if not session:
            raise InvalidSessionException("Session not found or expired")

        return ValidateSessionResponse(
            is_valid=True, user_id=session.user_id, session_id=session.id
        )
