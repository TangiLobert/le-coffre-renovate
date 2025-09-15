from typing import Dict, Any, Protocol, List, Union
from dataclasses import dataclass
from uuid import UUID


@dataclass
class Token:
    value: str
    user_id: Union[UUID, str]
    email: str
    roles: List[str]
    claims: Dict[str, Any]

    def has_role(self, role: str) -> bool:
        return role in self.roles


class TokenGateway(Protocol):
    async def generate_token(
        self,
        user_id: Union[UUID, str],
        email: str,
        roles: List[str],
        claims: Dict[str, Any] | None = None,
    ) -> Token: ...

    async def validate_token(self, token: str) -> Token | None: ...
