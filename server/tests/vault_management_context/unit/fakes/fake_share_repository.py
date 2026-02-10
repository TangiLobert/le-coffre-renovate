from typing import List
from vault_management_context.application.gateways import ShareRepository
from vault_management_context.domain.entities import Share


class FakeShareRepository(ShareRepository):
    def __init__(self):
        self._shares: List[Share] = []

    def get_all(self) -> List[Share]:
        return self._shares.copy()

    def add(self, shares: List[Share]) -> None:
        self._shares.extend(shares)

    def clear(self) -> None:
        self._shares = []
