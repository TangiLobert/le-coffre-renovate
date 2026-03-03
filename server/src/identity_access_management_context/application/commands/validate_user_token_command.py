from dataclasses import dataclass
from typing import List


@dataclass
class ValidateUserTokenCommand:
    jwt_token: str
    required_roles: list[str] | None = None
