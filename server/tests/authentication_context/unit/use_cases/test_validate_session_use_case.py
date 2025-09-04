import pytest
from uuid import UUID

from authentication_context.application.use_cases import ValidateSessionUseCase
from authentication_context.domain.entities import AuthenticationSession
from authentication_context.domain.exceptions import InvalidSessionException


@pytest.fixture
def use_case(session_repository, jwt_token_gateway):
    return ValidateSessionUseCase(session_repository, jwt_token_gateway)


@pytest.mark.asyncio
async def test_should_validate_session_with_correct_token(
    use_case: ValidateSessionUseCase, session_repository, jwt_token_gateway
):
    user_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    jwt_token = "jwt_token_for_user@lecoffre.com_abc123"

    session = AuthenticationSession(user_id=user_id, jwt_token=jwt_token)
    session_repository.save(session)

    jwt_token_gateway.set_valid_token(
        jwt_token, {"user_id": str(user_id), "email": "user@lecoffre.com"}
    )

    response = await use_case.execute(jwt_token)

    assert response.is_valid is True
    assert response.user_id == user_id
    assert response.session_id == session.id


@pytest.mark.asyncio
async def test_should_invalidate_session_with_invalid_token(
    use_case: ValidateSessionUseCase, session_repository
):
    user_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    stored_token = "jwt_token_for_user@lecoffre.com_abc123"
    wrong_token = "wrong_token_xyz789"

    session = AuthenticationSession(user_id=user_id, jwt_token=stored_token)
    session_repository.save(session)

    with pytest.raises(InvalidSessionException):
        await use_case.execute(wrong_token)


@pytest.mark.asyncio
async def test_should_invalidate_session_with_token_not_in_session(
    use_case: ValidateSessionUseCase,
):
    token = "jwt_token_for_user@lecoffre.com_abc123"

    with pytest.raises(InvalidSessionException):
        await use_case.execute(token)


@pytest.mark.asyncio
async def test_should_invalidate_session_when_token_is_not_last_session(
    use_case: ValidateSessionUseCase, session_repository
):
    user_id = UUID("7d742e0e-bb76-4728-83ef-8d546d7c62e5")
    old_token = "jwt_token_for_user@lecoffre.com_old123"
    current_token = "jwt_token_for_user@lecoffre.com_new456"

    old_session = AuthenticationSession(user_id=user_id, jwt_token=old_token)
    session_repository.save(old_session)

    current_session = AuthenticationSession(user_id=user_id, jwt_token=current_token)
    session_repository.save(current_session)

    with pytest.raises(InvalidSessionException):
        await use_case.execute(old_token)
