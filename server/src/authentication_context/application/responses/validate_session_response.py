from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass
class ValidateSessionResponse:
    is_valid: bool
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
