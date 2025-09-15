from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
import logging

from user_management_context.adapters.input.fastapi.app_dependencies import (
    get_delete_user_usecase,
)
from user_management_context.application.use_cases import DeleteUserUseCase
from user_management_context.domain.exceptions import (
    UserNotFoundError,
)

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete a user by ID",
)
def delete_user(
    user_id: UUID,
    usecase: DeleteUserUseCase = Depends(get_delete_user_usecase),
):
    """
    Delete a user by its ID.

    - **user_id**: The ID of the user to delete

    Returns status code 204 (No Content) on successful deletion.
    """
    try:
        usecase.execute(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")
