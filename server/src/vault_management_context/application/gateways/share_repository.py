from typing import List, Protocol
from vault_management_context.domain.entities import Share


class ShareRepository(Protocol):
    def get_all(self) -> List[Share]: ...

    def add(self, shares: List[Share]) -> None: ...

    def clear(self) -> None: ...
